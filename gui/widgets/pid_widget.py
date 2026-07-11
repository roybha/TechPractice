from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem
from gui.style import AppStyles
from core.models.analysis import AnalysisResult
from gui.widgets.table_factory import TableFactory

class PIDWidget(QWidget):
    """
        Displays three tables:
          1. Recommended P / I / D / FF values (current → recommended)
          2. Change summary with ↑↓ arrows and status per coefficient
          3. Flight metrics (overshoot, rise time, settling, oscillation)
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{AppStyles.BG_DARK};")
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(6)

    def refresh(self, result: AnalysisResult):
        self._clear()
        self._add_recommendations(result)
        self._add_change_summary(result)
        self._add_flight_metrics(result)
        self._layout.addStretch()

    def _add_recommendations(self, result: AnalysisResult):
        tf = TableFactory
        lay = self._layout
        lay.addWidget(tf.section_label(
            "Recommended PID values  →  enter these in Betaflight"))

        headers = ["Axis", "P curr", "P rec", "I curr", "I rec",
                   "D curr", "D rec", "FF rec", "Priority"]
        recs = result.pid_recommendations
        t = tf.table(headers, len(recs), 30)

        for r, rec in enumerate(recs):
            pc = AppStyles.GREEN if rec.p_percent_change >= 0 else AppStyles.RED
            ic = AppStyles.GREEN if rec.i_percent_change >= 0 else AppStyles.RED
            dc = AppStyles.GREEN if rec.d_percent_change >= 0 else AppStyles.RED
            t.setItem(r, 0, tf.cell(rec.axis_name, AppStyles.CYAN, bold=True))
            t.setItem(r, 1, tf.cell(f"{rec.p_current:.0f}", AppStyles.MUTED))
            t.setItem(r, 2, tf.cell(f"{rec.p_recommended:.0f}", pc, bold=True))
            t.setItem(r, 3, tf.cell(f"{rec.i_current:.0f}", AppStyles.MUTED))
            t.setItem(r, 4, tf.cell(f"{rec.i_recommended:.0f}", ic, bold=True))
            t.setItem(r, 5, tf.cell(f"{rec.d_current:.0f}", AppStyles.MUTED))
            t.setItem(r, 6, tf.cell(f"{rec.d_recommended:.0f}", dc, bold=True))
            t.setItem(r, 7, tf.cell(f"{rec.feedforward_recommended:.0f}", AppStyles.AMBER, bold=True))
            t.setItem(r, 8, tf.cell(rec.part_change_priority, AppStyles.AMBER))
        lay.addWidget(t)

    def _add_change_summary(self, result: AnalysisResult):
        tf = TableFactory
        lay = self._layout
        lay.addWidget(tf.section_label(
            "Change summary  (↑ increase  ↓ decrease  · unchanged)"))

        recs = result.pid_recommendations
        t = tf.table(["Axis", "ΔP", "ΔI", "ΔD",
                      "P status", "I status", "D status"], len(recs))
        for r, rec in enumerate(recs):
            m = result.axis_metrics[rec.axis_name]
            t.setItem(r, 0, tf.cell(rec.axis_name, AppStyles.CYAN))
            t.setItem(r, 1, self._pct_cell(rec.p_percent_change))
            t.setItem(r, 2, self._pct_cell(rec.i_percent_change))
            t.setItem(r, 3, self._pct_cell(rec.d_percent_change))
            t.setItem(r, 4, self._status_cell(m.p_part))
            t.setItem(r, 5, self._status_cell(m.i_part))
            t.setItem(r, 6, self._status_cell(m.d_part))
        lay.addWidget(t)

    def _add_flight_metrics(self, result: AnalysisResult):
        tf = TableFactory
        lay = self._layout
        lay.addWidget(tf.section_label("Flight metrics  (measured from log)"))

        metrics = result.axis_metrics
        t = tf.table(["Axis", "Overshoot", "Rise time",
                      "Settling", "Oscillation"], len(metrics))
        for r, (axis, m) in enumerate(metrics.items()):
            ov_c = (AppStyles.RED if m.overshoot_percents > 0.20 else
                    AppStyles.AMBER if m.overshoot_percents > 0.10 else AppStyles.GREEN)
            osc = (f"{m.oscillation_frequency:.0f} Hz"
                   if m.oscillation_is_detected else "Clean")
            osc_col = AppStyles.RED if m.oscillation_is_detected else AppStyles.GREEN

            t.setItem(r, 0, tf.cell(axis, AppStyles.CYAN))
            t.setItem(r, 1, tf.cell(f"{m.overshoot_percents * 100:.1f}%", ov_c))
            t.setItem(r, 2, tf.cell(f"{m.rise_time_seconds * 1000:.0f} ms", AppStyles.TEXT))
            t.setItem(r, 3, tf.cell(f"{m.settling_time_seconds * 1000:.0f} ms", AppStyles.TEXT))
            t.setItem(r, 4, tf.cell(osc, osc_col))
        lay.addWidget(t)

    @staticmethod
    def _pct_cell(val: float) -> QTableWidgetItem:
        arrow = "↑" if val > 2 else ("↓" if val < -2 else "·")
        color = AppStyles.GREEN if val > 2 else (AppStyles.RED if val < -2 else AppStyles.MUTED)
        return TableFactory.cell(f"{arrow} {abs(val):.0f}%",
                                 color, bold=abs(val) > 2)

    @staticmethod
    def _status_cell(status: str) -> QTableWidgetItem:
        color = (AppStyles.RED if "High" in status else
                 AppStyles.AMBER if "Low" in status else AppStyles.GREEN)
        return TableFactory.cell(status, color)

    def _clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()