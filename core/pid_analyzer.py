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
    STEP_THRESHOLD = 0.5 # deg/s min change to count a step
    MIN_STEP_SEPARATION = 50 # difference between two different steps
    ANALYSIS_WINDOW_SECONDS = 3.0 # seconds of response to examine after each step
    OVERSHOOT_OK = 0.10 # 10%
    OVERSHOOT_WARNING = 0.20 # 20%
    SETTLING_OK_SECONDS = 0.5
    SETTLING_WARNING_SECONDS = 1.0
    STEADY_OK = 0.02 # 2%
    STEADY_WARNING = 0.05 # 5%
    OSCILLATION_SNR = 5.0 # peak must be Nx above mean PSD to count