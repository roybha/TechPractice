import numpy as np
from scipy import signal as scipy_signal
from core.models.metrics import AxisMetrics

class PIDAnalyzer:
    """
    Analyzes the quality of PID controller response for one flight axis.

    Takes raw gyro (actual) and setpoint arrays from FlightData,
    finds step changes in the setpoint, and measures how well
    the drone tracked each step.

    Key metrics explained:
    ─────────────────────────────────────────────────────────────────
    Overshoot   — how much the actual value exceeds the setpoint
                  after a step command. >10% = P too high or D too low.

    Rise time   — how fast the drone reaches 90 % of the commanded value.
                  Slow rise = P too low.

    Settling    — how long until the error stays within ±5 % of the step.
                 Long settling = I too low or D too low.

    Steady-state error — average residual error after settling.
                  >5 % = I too low.

    Oscillation — periodic wobble in the error signal detected via PSD.
                  High-frequency (>20 Hz) = D too high or LPF needed.
                  Low-frequency (<15 Hz)  = P too high.
    """
    # thresholds, that can be tuned
    STEP_THRESHOLD = 50.0 # setpoint is in deg/s change to count a step
    MIN_STEP_GAP_SECONDS = 0.05 # difference between two different steps
    ANALYSIS_WINDOW_SECONDS = 0.5 # seconds of response to examine after each step
    OVERSHOOT_OK = 0.10 # 10%
    OVERSHOOT_WARNING = 0.20 # 20%
    SETTLING_OK_SECONDS = 0.15 # 150 ms
    SETTLING_WARNING_SECONDS = 0.30 # 300 ms
    STEADY_OK = 0.02 # 2%
    STEADY_WARNING = 0.05 # 5%
    OSCILLATION_SNR = 5.0 # peak must be Nx above mean PSD to count\

    # betaflight oscillation bands (deg/s units, high sample rate)
    P_OSC_FREQ_MAX = 50.0  # below this - P-induced oscillation
    D_OSC_FREQ_MIN = 50.0  # above this - D-induced / needs filter

    # ignore pilot input frequencies (below this = not an oscillation)
    MIN_OSC_FREQ = 10.0


def _get_data(self, timestamp: np.ndarray) -> float:
    """Converts any timestamp unit to seconds per sample."""
    raw_data = float(np.mean(np.diff(timestamp)))

    # microseconds is a typical Betaflight value: 125–500 µs per sample
    if raw_data > 100:
        return raw_data / 1_000_000.0

    # milliseconds (unlikely for Betaflight)
    if raw_data > 0.1:
        return raw_data / 1_000.0

    # already seconds
    return raw_data


def _find_steps(self, setpoint: np.ndarray, fs: float) -> list[int]:
    """Returns indices where the stick input changes sharply."""
    diff = np.abs(np.diff(setpoint))
    raw_indices = np.where(diff > self.STEP_THRESHOLD)[0]

    if len(raw_indices) == 0:
        return []

    min_gap_samples = int(self.MIN_STEP_GAP_SEC * fs)

    filtered = [int(raw_indices[0])]
    for idx in raw_indices[1:]:
        if idx - filtered[-1] > min_gap_samples:
            filtered.append(int(idx))

    return filtered