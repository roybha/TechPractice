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

    def _calculate_filters(self, metrics: FilterMetrics) -> FilterRecommendation:
        reasoning = []

        if metrics.dominant_noise_frequency == 0.0:
            reasoning.append(
                "No dominant noise frequency detected. Gyroscope data is exceptionally clean or log is incomplete.")
            return FilterRecommendation(
                recommended_lpf_cutoff=0.0,
                recommended_notch_center=0.0,
                recommended_notch_bandwidth=0.0,
                reasoning=reasoning
            )

        notch_center = metrics.dominant_noise_frequency
        notch_bandwidth = notch_center * 0.15
        lpf_cutoff = notch_center * 0.75

        reasoning.append(
            f"Primary resonance detected at {notch_center:.1f} Hz. "
            "Applied Notch filter to mitigate high-frequency motor and frame noise."
        )

        return FilterRecommendation(
            recommended_lpf_cutoff=round(lpf_cutoff, 1),
            recommended_notch_center=round(notch_center, 1),
            recommended_notch_bandwidth=round(notch_bandwidth, 1),
            reasoning=reasoning
        )

    def _calculate_pids(self, axis_name: str, profile: DroneProfile) -> PIDRecommendation:
        reasoning = []
        p_change, i_change, d_change = 0.0, 0.0, 0.0

        # ultra heavy platforms (13-15 inches, >7kg total mass)
        if profile.prop_size_inches >= 13.0 or profile.weight_grams >= 7000:
            d_change = 25.0
            p_change = -5.0
            reasoning.append(
                "Ultra-heavy platform (13-15 inch class) detected. Significantly increasing D-term for inertia compensation and slightly reducing P-term to prevent low-frequency oscillations."
            )
        # heavy payload platforms (10 inch class, up to 4kg payload)
        elif profile.prop_size_inches >= 10.0 or profile.weight_grams >= 4000:
            d_change = 15.0
            reasoning.append(
                "Heavy payload platform (10 inch class) detected. Increasing D-term to ensure stable braking under load."
            )
        # standard tactical platforms (7-8 inch class, 1.5-2kg payload)
        elif profile.prop_size_inches >= 7.0:
            d_change = 5.0
            reasoning.append(
                "Tactical platform (7-8 inch class) detected. Minor D-term adjustment for payload stabilization."
            )
        else:
            reasoning.append("Sub-7-inch platform detected. Base PID multipliers remain unchanged.")

        return PIDRecommendation(
            axis_name=axis_name,
            p_current=0.0,
            i_current=0.0,
            d_current=0.0,
            p_percent_change=p_change,
            i_percent_change=i_change,
            d_percent_change=d_change,
            p_recommended=0.0,
            i_recommended=0.0,
            d_recommended=0.0,
            reasoning=reasoning,
            part_change_priority="D" if d_change > 0 else "P"
        )

    def analyze(self, flight_data: FlightData, profile: DroneProfile) -> AnalysisResult:
        analyzer = FFTAnalyzer()

        axes = {
            "Roll": flight_data.gyro_roll,
            "Pitch": flight_data.gyro_pitch,
            "Yaw": flight_data.gyro_yaw
        }

        filter_metrics_dict = {}
        filter_recs_dict = {}
        pid_recs_list = []
        global_assessment = "Flight dynamics are within standard operational parameters."

        for axis_name, gyro_array in axes.items():
            f_metrics = analyzer.analyze_axis(axis_name, gyro_array, flight_data.sample_rate_hz)
            filter_metrics_dict[axis_name] = f_metrics

            filter_recs_dict[axis_name] = self._calculate_filters(f_metrics)
            pid_recs_list.append(self._calculate_pids(axis_name, profile))

            if 0 < f_metrics.dominant_noise_frequency < 50.0:
                global_assessment = (
                    f"CRITICAL STRUCTURAL WARNING: Low-frequency oscillations ({f_metrics.dominant_noise_frequency:.1f} Hz) "
                    f"detected on the {axis_name} axis. Indicates severe mechanical compliance, loose hardware, or frame fracture. "
                    "Software filtering is ineffective. Immediate hardware inspection required."
                )

        pid_analyzer = PIDAnalyzer()

        axis_metrics = {
            "Roll": pid_analyzer.analyze_axis(
                "Roll",
                flight_data.setpoint_roll,
                flight_data.gyro_roll,
                flight_data.timestamp,
            ),
            "Pitch": pid_analyzer.analyze_axis(
                "Pitch",
                flight_data.setpoint_pitch,
                flight_data.gyro_pitch,
                flight_data.timestamp,
            ),
            "Yaw": pid_analyzer.analyze_axis(
                "Yaw",
                flight_data.setpoint_yaw,
                flight_data.gyro_yaw,
                flight_data.timestamp,
            ),
        }

        return AnalysisResult(
            flight_data=flight_data,
            axis_metrics=axis_metrics,
            filter_metrics=filter_metrics_dict,
            overall_quality_score=85.0 if "CRITICAL" not in global_assessment else 20.0,
            overall_assessment=global_assessment,
            pid_recommendations=pid_recs_list,
            filter_recommendation=filter_recs_dict["Roll"]
        )