import numpy as np
from scipy import signal as scipy_signal
from core.models.metrics import AxisMetrics


class PIDAnalyzer:
    """
    Analyzes PID response quality from Betaflight Blackbox logs.

    Input:  setpoint[0/1/2] and gyroADC[0/1/2] columns (deg/s), timestamp in microseconds.
    Output: AxisMetrics with overshoot, rise time, settling time, steady-state error, oscillation.
    """

    STEP_THRESHOLD = 50.0  # minimum deg/s change to count as a stick input
    MIN_STEP_GAP_SECONDS = 0.05  # minimum time between two separate manoeuvres
    ANALYSIS_WINDOW_SECONDS = 0.5  # how long to observe the response after each step

    OVERSHOOT_WARNING = 0.20  # >20% → P too high
    SETTLING_WARNING_SECONDS = 0.30  # >300 ms → I/D too low
    STEADY_WARNING = 0.05  # >5% residual error → I too low
    OSCILLATION_SNR = 5.0  # peak must exceed mean PSD by this factor

    MIN_OSC_FREQ = 10.0  # below this = pilot input, not oscillation
    P_OSC_MAX_HZ = 50.0  # 10–50 Hz peak → P too high
    D_OSC_MIN_HZ = 50.0  # 50–400 Hz peak → D too high / needs filter

    def analyze_axis(
            self,
            axis_name: str,
            setpoint: np.ndarray,
            gyro: np.ndarray,
            timestamp: np.ndarray,
    ) -> AxisMetrics:
        dt = self._get_dt(timestamp)
        fs = 1.0 / dt

        step_indices = self._find_steps(setpoint, fs)
        osc, osc_freq = self._detect_oscillation(setpoint, gyro, dt)

        if not step_indices:
            return self._build_metrics(axis_name, 0, 0, 0, 0, osc, osc_freq)

        overshoots, rise_times, settlings, steady_errs = [], [], [], []
        for idx in step_indices:
            r = self._analyze_one_step(setpoint, gyro, idx, dt)
            if r is not None:
                overshoots.append(r["overshoot"])
                rise_times.append(r["rise_time"])
                settlings.append(r["settling"])
                steady_errs.append(r["steady_err"])

        if not overshoots:
            return self._build_metrics(axis_name, 0, 0, 0, 0, osc, osc_freq)

        return self._build_metrics(
            axis_name,
            overshoot=float(np.mean(overshoots)),
            rise_time=float(np.mean(rise_times)),
            settling=float(np.mean(settlings)),
            steady_err=float(np.mean(steady_errs)),
            osc=osc,
            osc_freq=osc_freq,
        )

    @staticmethod
    def _get_dt(timestamp: np.ndarray) -> float:
        """Converts any timestamp unit to seconds per sample."""
        raw = float(np.mean(np.diff(timestamp)))
        if raw > 100:   return raw / 1_000_000.0  # microseconds (Betaflight default)
        if raw > 0.1:   return raw / 1_000.0  # milliseconds
        return raw  # already seconds

    def _find_steps(self, setpoint: np.ndarray, fs: float) -> list[int]:
        """Returns indices where the stick input changes sharply."""
        diff = np.abs(np.diff(setpoint))
        raw = np.where(diff > self.STEP_THRESHOLD)[0]

        if len(raw) == 0:
            return []

        gap = int(self.MIN_STEP_GAP_SECONDS * fs)
        filtered = [int(raw[0])]
        for idx in raw[1:]:
            if idx - filtered[-1] > gap:
                filtered.append(int(idx))
        return filtered

    def _analyze_one_step(
            self,
            setpoint: np.ndarray,
            gyro: np.ndarray,
            step_idx: int,
            dt: float,
    ) -> dict | None:
        """Measures overshoot, rise time, settling and steady-state error for one manoeuvre."""
        fs = 1.0 / dt
        window = int(self.ANALYSIS_WINDOW_SECONDS * fs)
        end = min(step_idx + window, len(setpoint) - 1)

        if end - step_idx < int(0.02 * fs):
            return None

        sp_win = setpoint[step_idx:end]
        gy_win = gyro[step_idx:end]

        sp_before = float(np.mean(setpoint[max(0, step_idx - 10):step_idx]))

        p0, p1 = int(0.005 * fs), int(0.025 * fs)
        if p1 >= len(sp_win):
            return None

        sp_after = float(np.mean(sp_win[p0:p1]))
        step_mag = abs(sp_after - sp_before)

        if step_mag < 20.0:
            return None

        going_up = sp_after > sp_before

        peak = float(gy_win.max()) if going_up else float(gy_win.min())
        overshoot = max(0.0, (peak - sp_after if going_up else sp_after - peak) / step_mag)

        target = sp_before + 0.9 * (sp_after - sp_before)
        rise_time = self.ANALYSIS_WINDOW_SECONDS

        # FIX: Avoided enumerate() to bypass PyCharm's tuple[int, Any] type hinting bug
        for i in range(len(gy_win)):
            v = float(gy_win[i])
            if (going_up and v >= target) or (not going_up and v <= target):
                rise_time = i * dt
                break

        tolerance = 0.05 * step_mag
        settling_time = self.ANALYSIS_WINDOW_SECONDS
        for i in range(len(gy_win) - 1, 0, -1):
            if abs(gy_win[i] - sp_after) > tolerance:
                settling_time = i * dt
                break
        else:
            settling_time = 0.0

        g3 = gy_win[2 * len(gy_win) // 3:]
        s3 = sp_win[2 * len(sp_win) // 3:]
        steady_err = float(np.mean(np.abs(g3 - s3))) / step_mag

        return dict(
            overshoot=overshoot,
            rise_time=rise_time,
            settling=settling_time,
            steady_err=steady_err,
        )

    def _detect_oscillation(
            self,
            setpoint: np.ndarray,
            gyro: np.ndarray,
            dt: float,
    ) -> tuple[bool, float]:
        """Detects periodic wobble in the tracking error using Welch PSD."""
        if len(gyro) < 512:
            return False, 0.0

        fs = 1.0 / dt
        error = gyro - setpoint

        n_per_seg = min(4096, len(error) // 8)
        freqs, psd = scipy_signal.welch(error, fs=fs, nperseg=n_per_seg, window="hann")

        # FIX: Explicit casting to np.asarray enforces instance typing for PyCharm
        freqs_arr = np.asarray(freqs)
        psd_arr = np.asarray(psd)

        # FIX: Idiomatic boolean masking instead of .tolist() anti-pattern
        band = (freqs_arr >= self.MIN_OSC_FREQ) & (freqs_arr <= 400.0)
        freqs_b = freqs_arr[band]
        psd_b = psd_arr[band]

        if len(freqs_b) == 0:
            return False, 0.0

        peak_idx = int(np.argmax(psd_b))
        peak_power = float(psd_b[peak_idx])
        peak_freq = float(freqs_b[peak_idx])
        is_osc = peak_power > self.OSCILLATION_SNR * float(np.mean(psd_b))

        return is_osc, (peak_freq if is_osc else 0.0)

    def _assess_p(self, overshoot: float, osc: bool, osc_freq: float) -> str:
        if osc and self.MIN_OSC_FREQ <= osc_freq <= self.P_OSC_MAX_HZ:
            return "Too High"
        if overshoot > self.OVERSHOOT_WARNING:
            return "Too High"
        if overshoot < 0.02 and not osc:
            return "Too Low"
        return "Good"

    def _assess_i(self, steady_err: float, settling: float) -> str:
        if steady_err > self.STEADY_WARNING or settling > self.SETTLING_WARNING_SECONDS:
            return "Too Low"
        return "Good"

    def _assess_d(self, osc: bool, osc_freq: float, overshoot: float) -> str:
        if osc and osc_freq >= self.D_OSC_MIN_HZ:
            return "Too High"
        if overshoot > self.OVERSHOOT_WARNING and not osc:
            return "Too Low"
        return "Good"

    def _build_metrics(
            self,
            axis_name: str,
            overshoot: float,
            rise_time: float,
            settling: float,
            steady_err: float,
            osc: bool,
            osc_freq: float,
    ) -> AxisMetrics:
        return AxisMetrics(
            axis_name=axis_name,
            overshoot_percents=overshoot,
            rise_time_seconds=rise_time,
            settling_time_seconds=settling,
            steady_state_error=steady_err,
            oscillation_is_detected=osc,
            oscillation_frequency=osc_freq,
            p_part=self._assess_p(overshoot, osc, osc_freq),
            i_part=self._assess_i(steady_err, settling),
            d_part=self._assess_d(osc, osc_freq, overshoot),
        )