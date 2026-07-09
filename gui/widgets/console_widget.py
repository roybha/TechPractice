from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton

from core.models.analysis import AnalysisResult


class ConsoleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.console: QTextEdit = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setObjectName('consoleOutput')
        self.console.setText('Awaiting data...')
        layout.addWidget(self.console)

        # Clear button
        button_layout = QHBoxLayout()
        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.console.clear)
        button_layout.addStretch()
        button_layout.addWidget(clear_button)
        layout.addLayout(button_layout)

    def log(self, text:str):
        self.console.append(text)

    def display_result(self, result: AnalysisResult):
        self.clear()
        self.log("=" * 60)
        self.log("  TUNING REPORT")
        self.log("=" * 60)
        self.log(f"\n[STATUS]  {result.overall_assessment}")
        self.log(f"[SCORE]   {result.overall_quality_score:.0f} / 100\n")

        # Call of private methods
        self._display_pid_recommendations(result)
        self._display_filter_settings(result)
        self._display_flight_metrics(result)

    def _display_pid_recommendations(self, result: AnalysisResult):
        self.log("─" * 64)
        self.log("  PID RECOMMENDATIONS ")
        self.log("─" * 64)
        self.log(f"  {'AXIS':<8} {'P':>6} {'I':>6} {'D':>6} {'FF':>6}   CHANGE")
        self.log(f"  {'────':<8} {'──':>6} {'──':>6} {'──':>6} {'──':>6}")

        for rec in result.pid_recommendations:
            p_arrow = "↓" if rec.p_percent_change < -2 else ("↑" if rec.p_percent_change > 2 else "·")
            i_arrow = "↓" if rec.i_percent_change < -2 else ("↑" if rec.i_percent_change > 2 else "·")
            d_arrow = "↓" if rec.d_percent_change < -2 else ("↑" if rec.d_percent_change > 2 else "·")
            self.log(
                f"  {rec.axis_name:<8}"
                f" {rec.p_recommended:>5.0f}{p_arrow}"
                f" {rec.i_recommended:>5.0f}{i_arrow}"
                f" {rec.d_recommended:>5.0f}{d_arrow}"
                f" {rec.feedforward_recommended:>5.0f}"
                f"   priority: {rec.part_change_priority}"
            )

        self.log("")
        for rec in result.pid_recommendations:
            self.log(f"  [{rec.axis_name}] reasoning:")
            for r in rec.reasoning:
                self.log(f"    → {r}")
        self.log("")

    def _display_filter_settings(self, result: AnalysisResult):
        fr = result.filter_recommendation
        if not fr:
            return

        self.log("─" * 64)
        self.log("  FILTER RECOMMENDATIONS)")
        self.log("─" * 64)

        self.log("\n  GYRO LOWPASS (Dynamic):")
        self.log(f"    Gyro LPF1 Dynamic Min Cutoff : {fr.gyro_lpf_min_hz:.0f} Hz")
        self.log(f"    Gyro LPF1 Dynamic Max Cutoff : {fr.gyro_lpf_max_hz:.0f} Hz")

        if fr.gyro_notch1_center_hz > 0:
            self.log("\n  GYRO NOTCH FILTERS:")
            self.log(f"    Notch 1 Center  : {fr.gyro_notch1_center_hz:.0f} Hz")
            self.log(f"    Notch 1 Cutoff  : {fr.gyro_notch1_cutoff_hz:.0f} Hz")
        if fr.gyro_notch2_center_hz > 0:
            self.log(f"    Notch 2 Center  : {fr.gyro_notch2_center_hz:.0f} Hz")
            self.log(f"    Notch 2 Cutoff  : {fr.gyro_notch2_cutoff_hz:.0f} Hz")

        self.log("\n  RPM FILTER  (most effective — enable this first):")
        self.log(f"    Harmonics       : {fr.rpm_filter_harmonics}")
        self.log(f"    Min Frequency   : {fr.rpm_filter_min_hz:.0f} Hz")

        self.log("\n  D-TERM LOWPASS:")
        self.log(f"    LPF1 Dyn Min    : {fr.dterm_lpf1_min_hz:.0f} Hz")
        self.log(f"    LPF1 Dyn Max    : {fr.dterm_lpf1_max_hz:.0f} Hz")
        self.log(f"    LPF2 Static     : {fr.dterm_lpf2_hz:.0f} Hz")

        self.log("\n  YAW LOWPASS:")
        self.log(f"    Yaw LPF Cutoff  : {fr.yaw_lpf_hz:.0f} Hz")

        self.log("\n  Filter reasoning:")
        for r in fr.reasoning:
            self.log(f"    → {r}")
        self.log("")

    def _display_flight_metrics(self, result: AnalysisResult):
        self.log("─" * 64)
        self.log("  CURRENT FLIGHT METRICS ")
        self.log("─" * 64)
        for axis_name, m in result.axis_metrics.items():
            self.log(f"\n  [{axis_name}]")
            self.log(f"    Overshoot   : {m.overshoot_percents * 100:.1f}%   P → {m.p_part}")
            self.log(f"    Rise time   : {m.rise_time_seconds * 1000:.0f} ms")
            self.log(f"    Settling    : {m.settling_time_seconds * 1000:.0f} ms  I → {m.i_part}")
            osc = f"{m.oscillation_frequency:.0f} Hz" if m.oscillation_is_detected else "Clean"
            self.log(f"    Oscillation : {osc}   D → {m.d_part}")

    def clear(self):
        self.console.clear()