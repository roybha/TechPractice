from email.policy import default

from core.models.flight import FlightData
from core.models.drone_profile import DroneProfile
from core.models.metrics import FilterMetrics, AxisMetrics
from core.models.recommendations import PIDRecommendation, FilterRecommendation
from core.models.analysis import AnalysisResult
from core.fft_analyzer import FFTAnalyzer
from core.pid_analyzer import PIDAnalyzer

_SIZE_CLASSES = [
    # 15" ultra-heavy (>7 kg) — large payload UAVs
    {
        "label": "15\" Ultra-Heavy (>7 kg)",
        "prop_min": 15.0, "weight_min": 7000,
        "Roll":  {"P": 16, "I": 40, "D": 70, "FF": 0},
        "Pitch": {"P": 18, "I": 45, "D": 76, "FF": 0},
        "Yaw":   {"P": 20, "I": 38, "D":  0, "FF": 65},
    },
    # 13" heavy (5–7 kg)
    {
        "label": "13\" Heavy (5–7 kg)",
        "prop_min": 13.0, "weight_min": 5000,
        "Roll":  {"P": 22, "I": 52, "D": 60, "FF": 0},
        "Pitch": {"P": 24, "I": 57, "D": 65, "FF": 0},
        "Yaw":   {"P": 25, "I": 48, "D":  0, "FF": 60},
    },
    # 10" medium-heavy (3–5 kg)
    {
        "label": "10\" Medium-Heavy (3–5 kg)",
        "prop_min": 10.0, "weight_min": 3000,
        "Roll":  {"P": 28, "I": 60, "D": 52, "FF": 0},
        "Pitch": {"P": 30, "I": 65, "D": 56, "FF": 0},
        "Yaw":   {"P": 30, "I": 55, "D":  0, "FF": 55},
    },
    # 7–10" medium (1.5–3 kg)
    {
        "label": "7–10\" Medium (1.5–3 kg)",
        "prop_min": 7.0, "weight_min": 1500,
        "Roll":  {"P": 38, "I": 72, "D": 42, "FF": 0},
        "Pitch": {"P": 40, "I": 78, "D": 46, "FF": 0},
        "Yaw":   {"P": 38, "I": 68, "D":  0, "FF": 40},
    },
    # 5–7" standard (<1.5 kg)
    {
        "label": "5–7\" Standard (<1.5 kg)",
        "prop_min": 0.0, "weight_min": 0,
        "Roll":  {"P": 45, "I": 80, "D": 35, "FF": 0},
        "Pitch": {"P": 47, "I": 85, "D": 38, "FF": 0},
        "Yaw":   {"P": 45, "I": 80, "D":  0, "FF": 0},
    },
]
class TuningEngine:
    def _get_size_class(self, profile: DroneProfile) -> dict:
        """
        Matches drone to size class by BOTH prop size AND weight.
        Both conditions must be met — prevents misclassification
        (e.g. a light 10" shouldn't be treated as heavy 13").
        """
        for cls in _SIZE_CLASSES:
            if (profile.prop_size_inches >= cls["prop_min"] and
                    profile.weight_grams >= cls["weight_min"]):
                return cls
        return _SIZE_CLASSES[-1]  # fallback: smallest class

    def _collect_fft_peaks(self, filter_metrics: dict) -> list[float]:
        """Merges FFT peaks from all axes into one sorted, deduplicated list."""
        peaks = []
        for fm in filter_metrics.values():
            peaks.extend(fm.peak_frequencies)
        return sorted(set(round(f, 0) for f in peaks if f > 20))

    @staticmethod
    def _calc_rpm_filter(profile: DroneProfile, log: list) -> tuple[int, float]:
        pass

    @staticmethod
    def _calc_dynamic_notch(peaks: list, log: list) -> tuple[int, int, float, float]:
        pass

    @staticmethod
    def _calc_gyro_lpf(dominant_freq: float, profile: DroneProfile, log: list) -> tuple[float, float]:
        pass

    @staticmethod
    def _calc_static_notches(peaks: list, log: list) -> tuple[float, float, float, float]:
        pass

    @staticmethod
    def _calc_dterm_yaw(gyro_lpf_min: float, profile: DroneProfile, log: list) -> tuple[float, float, float, float]:
        pass

    def _calculate_filters(self, metrics: dict, profile: DroneProfile) -> FilterRecommendation:
        log = []
        peaks = self._collect_fft_peaks(metrics)
        dominant = max(
            (fm.dominant_noise_frequency for fm in metrics.values()), default=0.0
        )

        harmonics, rpm_min = self._calc_rpm_filter(profile, log)
        width, q, dn_min, dn_max = self._calc_dynamic_notch(peaks, log)
        lpf_min, lpf_max = self._calc_gyro_lpf(dominant, profile, log)
        n1c, n1cut, n2c, n2cut = self._calc_static_notches(peaks, log)
        dmin, dmax, dlpf2, yaw_lpf = self._calc_dterm_yaw(lpf_min, profile, log)

        return FilterRecommendation(
            gyro_lpf_min_hz=lpf_min, gyro_lpf_max_hz=lpf_max,
            gyro_notch1_center_hz=n1c, gyro_notch1_cutoff_hz=n1cut,
            gyro_notch2_center_hz=n2c, gyro_notch2_cutoff_hz=n2cut,
            rpm_filter_harmonics=harmonics, rpm_filter_min_hz=rpm_min,
            dyn_notch_width_pct=width, dyn_notch_q=q,
            dyn_notch_min_hz=dn_min, dyn_notch_max_hz=dn_max,
            dterm_lpf1_min_hz=dmin, dterm_lpf1_max_hz=dmax,
            dterm_lpf2_hz=dlpf2, yaw_lpf_hz=yaw_lpf,
            reasoning=log,
        )

    @staticmethod
    def _adjust_d(d: float, metrics: AxisMetrics, log: list) -> float:
        pass

    @staticmethod
    def _adjust_p(p: float, metrics: AxisMetrics, log: list) -> float:
        pass

    @staticmethod
    def _adjust_i(i: float, metrics: AxisMetrics, log: list) -> float:
        pass

    @staticmethod
    def _build_pid_recommendation(
            axis_name: str, defaults: dict,
            p: float, i: float, d: float, ff: float,
            log: list,
    ) -> PIDRecommendation:
        """Clamps values to safe Betaflight ranges and builds the dataclass."""
        p = round(max(8, min(p, 100)), 0)
        i = round(max(15, min(i, 200)), 0)
        d = round(max(0, min(d, 80)), 0)
        ff = round(max(0, min(ff, 200)), 0)

        pct = lambda rec, base: round((rec / base - 1) * 100, 1) if base > 0 else 0.0

        return PIDRecommendation(
            axis_name=axis_name,
            p_current=float(defaults["P"]), i_current=float(defaults["I"]),
            d_current=float(defaults["D"]), feedforward_current=float(defaults["FF"]),
            p_recommended=p, i_recommended=i,
            d_recommended=d, feedforward_recommended=ff,
            p_percent_change=pct(p, defaults["P"]),
            i_percent_change=pct(i, defaults["I"]),
            d_percent_change=pct(d, defaults["D"]) if defaults["D"] > 0 else 0.0,
            reasoning=log,
            part_change_priority=(
                "D" if abs(d / max(defaults["D"], 1) - 1) > 0.08 else
                "P" if abs(p / defaults["P"] - 1) > 0.05 else "I"
            ),
        )

    def _calculate_pids(self, axis_name: str, metrics: AxisMetrics, size_class: dict) -> PIDRecommendation:
        defaults = size_class[axis_name]
        p, i, d, ff = (float(defaults[k]) for k in ("P", "I", "D", "FF"))
        log = [f"Base ({size_class['label']}): P={p:.0f} I={i:.0f} D={d:.0f}"]

        d = self._adjust_d(d, metrics, log)
        p = self._adjust_p(p, metrics, log)
        i = self._adjust_i(i, metrics, log)

        if axis_name == "Yaw" and ff == 0:
            ff = 50.0
            log.append("Yaw FF=50: compensates for D=0")

        return self._build_pid_recommendation(axis_name, defaults, p, i, d, ff, log)

    def analyze(self, flight_data: FlightData, profile: DroneProfile) -> AnalysisResult:
        """Runs full analysis: FFT + PID metrics → filter + PID recommendations."""
        fft_analyzer = FFTAnalyzer()
        pid_analyzer = PIDAnalyzer()
        size_class = self._get_size_class(profile)

        axes = {
            "Roll": (flight_data.setpoint_roll, flight_data.gyro_roll),
            "Pitch": (flight_data.setpoint_pitch, flight_data.gyro_pitch),
            "Yaw": (flight_data.setpoint_yaw, flight_data.gyro_yaw),
        }

        axis_metrics: dict = {}
        filter_metrics: dict = {}
        pid_recs: list = []
        assessment = f"Size class: {size_class['label']}. Dynamics within expected parameters."

        for axis_name, (sp, gyro) in axes.items():
            am = pid_analyzer.analyze_axis(axis_name, sp, gyro, flight_data.timestamp)
            fm = fft_analyzer.analyze_axis(axis_name, gyro, flight_data.sample_rate_hz)
            axis_metrics[axis_name] = am
            filter_metrics[axis_name] = fm
            pid_recs.append(self._calculate_pids(axis_name, am, size_class))

            if 0 < fm.dominant_noise_frequency < 25.0:
                assessment = (
                    f"CRITICAL: {fm.dominant_noise_frequency:.0f} Hz low-freq noise on "
                    f"{axis_name}. Inspect hardware before flying."
                )

        filter_rec = self._calculate_filters(filter_metrics, profile)

        scores = []
        for am in axis_metrics.values():
            s = 100.0
            if am.overshoot_percents > 0.20:
                s -= 25
            elif am.overshoot_percents > 0.10:
                s -= 10
            if am.oscillation_is_detected:       s -= 20
            if am.settling_time_seconds > 0.40:  s -= 15
            if am.steady_state_error > 0.05:     s -= 10
            scores.append(max(0.0, s))

        return AnalysisResult(
            flight_data=flight_data,
            axis_metrics=axis_metrics,
            filter_metrics=filter_metrics,
            overall_quality_score=round(sum(scores) / len(scores), 1) if scores else 0.0,
            overall_assessment=assessment,
            pid_recommendations=pid_recs,
            filter_recommendation=filter_rec,
        )