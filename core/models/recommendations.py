from dataclasses import dataclass, field

@dataclass
class PIDRecommendation:
    axis_name: str

    # Current PID values
    p_current: float
    i_current: float
    d_current: float

    # Recommended % (can be negative)
    p_percent_change: float
    i_percent_change: float
    d_percent_change: float

    # Recommended absolute data
    p_recommended: float
    i_recommended: float
    d_recommended: float

    reasoning: list[str] = field(default_factory=list)
    part_change_priority: str = "P"


@dataclass
class FilterRecommendation:
    recommended_lpf_cutoff: float
    recommended_notch_center: float
    recommended_notch_bandwidth: float
    reasoning: list[str] = field(default_factory=list)
