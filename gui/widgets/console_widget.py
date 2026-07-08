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
        self.log("  DIAGNOSTIC REPORT")
        self.log("=" * 60)
        self.log(f"\n[STATUS]  {result.overall_assessment}")
        self.log(f"[SCORE]   {result.overall_quality_score:.0f} / 100\n")

        # Filteres
        self.log("FILTER RECOMMENDATIONS")
        fr = result.filter_recommendation
        if fr:
            self.log(f"  LPF cutoff:     {fr.recommended_lpf_cutoff:.1f} Hz")
            self.log(f"  Notch center:   {fr.recommended_notch_center:.1f} Hz")
            self.log(f"  Notch bandwidth:{fr.recommended_notch_bandwidth:.1f} Hz")
            for r in fr.reasoning:
                self.log(f"  → {r}")

        # PID by axis
        self.log("\nPID AXIS METRICS")
        for axis_name, m in result.axis_metrics.items():
            self.log(f"\n  [{axis_name}]")
            self.log(f"  Overshoot:    {m.overshoot_percents * 100:.1f}%  │  P: {m.p_part}")
            self.log(f"  Rise time:    {m.rise_time_seconds * 1000:.0f} ms")
            self.log(f"  Settling:     {m.settling_time_seconds * 1000:.0f} ms  │  I: {m.i_part}")
            osc_str = f"{m.oscillation_frequency:.1f} Hz" if m.oscillation_is_detected else "Clean"
            self.log(f"  Oscillation:  {osc_str}  │  D: {m.d_part}")

        # PID recommendations
        self.log("\nPID RECOMMENDATIONS")
        for rec in result.pid_recommendations:
            self.log(f"\n  [{rec.axis_name}]")
            self.log(f"  P: {rec.p_percent_change:+.0f}%  "
                     f"I: {rec.i_percent_change:+.0f}%  "
                     f"D: {rec.d_percent_change:+.0f}%")
            for r in rec.reasoning:
                self.log(f"  → {r}")

    def clear(self):
        self.console.clear()