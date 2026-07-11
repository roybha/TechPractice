from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from gui.style import AppStyles
from gui.widgets.pid_widget import PIDWidget
from gui.widgets.filter_widget import FilterWidget
from core.models.analysis import AnalysisResult

class ResultsWidget(QWidget):
    """
    Bottom panel. Composes PIDWidget and FilterWidget inside a QTabWidget.
    Also owns the score/status banner above the tabs.
    Responsibility: coordinate tab updates and banner state.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._banner = self._make_banner()
        layout.addWidget(self._banner)

        self._pid_tab    = PIDWidget()
        self._filter_tab = FilterWidget()

        tabs = QTabWidget()
        tabs.setStyleSheet(AppStyles.tab_style())   # ← fixed: tab-only QSS
        tabs.addTab(self._pid_tab,    "PID Tuning")
        tabs.addTab(self._filter_tab, "Filter Settings")
        layout.addWidget(tabs)

    @staticmethod
    def _make_banner() -> QLabel:
        lbl = QLabel("  Load a log to see recommendations.")
        lbl.setStyleSheet(AppStyles.banner_style(AppStyles.MUTED))
        return lbl

    def display_result(self, result: AnalysisResult):
        """Entry point called by MainWindow after every successful analysis."""
        self._update_banner(result)
        self._pid_tab.refresh(result)
        if result.filter_recommendation:
            self._filter_tab.refresh(result.filter_recommendation)

    def clear(self):
        self._banner.setText("  Load a log to see recommendations.")
        self._banner.setStyleSheet(AppStyles.banner_style(AppStyles.MUTED))

    def _update_banner(self, result: AnalysisResult):
        score = result.overall_quality_score
        color = (AppStyles.GREEN if score >= 80 else
                 AppStyles.AMBER if score >= 60 else AppStyles.RED)
        self._banner.setText(
            f"  Score: {score:.0f}/100   │   {result.overall_assessment}"
        )
        self._banner.setStyleSheet(AppStyles.banner_style(color))