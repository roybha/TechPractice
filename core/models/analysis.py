from dataclasses import dataclass, field
from .flight import FlightData
from .metrics import AxisMetrics, FilterMetrics
from .recommendations import PIDRecommendation, FilterRecommendation

@dataclass
class AnalysisResult:
    # Reference on an input data
    flight_data: FlightData

    axis_metrics: dict[str, AxisMetrics]  # Keys: "Roll", "Pitch", "Yaw"
    filter_metrics: dict[str, FilterMetrics]  # Keys: "X", "Y", "Z"

    overall_quality_score: float
    overall_assessment: str

    pid_recommendations: list[PIDRecommendation] = field(default_factory=list)
    filter_recommendation: FilterRecommendation | None = None