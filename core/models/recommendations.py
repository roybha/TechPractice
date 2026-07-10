from dataclasses import dataclass, field

@dataclass
class PIDRecommendation:
    axis_name: str

    # Current PID values
    p_current: float
    i_current: float
    d_current: float

    # Recommended % (can be negative)
    p_percent_change: float = 0.0
    i_percent_change: float = 0.0
    d_percent_change: float = 0.0

    # Recommended absolute data
    p_recommended: float = 0.0
    i_recommended: float = 0.0
    d_recommended: float = 0.0

    reasoning: list[str] = field(default_factory=list)
    part_change_priority: str = "P"
    feedforward_current: float = 0.0
    feedforward_recommended: float = 0.0


@dataclass
class FilterRecommendation:
    # Gyro LowPass (Dynamic)
    gyro_lpf_min_hz: float
    gyro_lpf_max_hz: float

    # Gyro Notch Filters
    gyro_notch1_center_hz: float  # gyro NF 1 center Frequency
    gyro_notch1_cutoff_hz: float  # gyro NF 1 cutoff Frequency
    gyro_notch2_center_hz: float  # gyro NF 2 center Frequency
    gyro_notch2_cutoff_hz: float  # gyro NF 2 cutoff Frequency

    # RPM Filter
    rpm_filter_harmonics: int # number of harmonics (1-3, usually 3)
    rpm_filter_min_hz: float  # min frequency to apply RPM filter

    # ── Dynamic Notch Filter ─────────────────────────────────────────
    dyn_notch_width_pct: int  # 0=auto, 8=typical manual
    dyn_notch_q: int  # 250=wide, 350=narrow
    dyn_notch_min_hz: float  # lower search bound
    dyn_notch_max_hz: float  # upper search bound

    # D-Term Lowpass
    dterm_lpf1_min_hz: float  # D Term Lowpass 1 dynamic min cutoff
    dterm_lpf1_max_hz: float  # D Term Lowpass 1 dynamic max cutoff
    dterm_lpf2_hz: float  # D Term Lowpass 2 static cutoff

    # Yaw Lowpass
    yaw_lpf_hz: float  # Yaw Lowpass cutoff

    reasoning: list[str] = field(default_factory=list)