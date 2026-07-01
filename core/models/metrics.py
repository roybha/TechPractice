from dataclasses import dataclass, field

@dataclass
class AxisMetrics:
    axis_name: str  # "Roll", "Pitch", "Yaw"

    # Main PID properties
    overshoot_percents: float
    rise_time_seconds: float
    settling_time_seconds: float
    steady_state_error: float

    # Data about oscillations (vibrations)
    oscillation_is_detected: bool
    oscillation_frequency: float  # Hz

    # PID parts assessment (ex: "Good", "Too High", "Too Low")
    p_part: str
    i_part: str
    d_part: str


@dataclass
class FilterMetrics:
    axis_name: str

    dominant_noise_frequency: float

    recommended_lpf_cutoff_frequency: float
    recommended_notch_frequency: float
    noise_amplitude: float

    peak_frequencies: list[float] = field(default_factory=list)
    peak_amplitudes: list[float] = field(default_factory=list)