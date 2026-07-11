from gui.style import AppStyles
from PyQt5.QtWidgets import (QWidget, QVBoxLayout,
                             QTabWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView,
                             QLabel)
from core.models.analysis import AnalysisResult
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from pid_widget import PIDWidget
from filter_widget import FilterWidget

class TableFactory:
    @staticmethod
    def cell(text: str, color: str = AppStyles.TEXT,
             bold: bool = False) -> QTableWidgetItem:
        it = QTableWidgetItem(str(text))
        it.setForeground(QColor(color))
        it.setFlags(Qt.ItemIsEnabled)
        if bold:
            f = QFont("Consolas", 11)
        f.setBold(True)
        it.setFont(f)
        return it

    @staticmethod
    def table(headers: list[str], rows: int,
              row_h: int = 28) -> QTableWidget:
        t = QTableWidget(rows, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionMode(QTableWidget.NoSelection)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setFixedHeight(34 + rows * row_h)
        t.setStyleSheet(AppStyles.get_stylesheet())
        return t

    @staticmethod
    def section_label(text: str) -> QLabel:
        lbl = QLabel(f"  {text}")
        lbl.setStyleSheet(
            f"background:#1C2B1C; color:{AppStyles.GREEN}; font-family:Consolas;"
            "font-size:12px; font-weight:bold; padding:5px; border-radius:3px;"
        )
        return lbl

    @staticmethod
    def setting_table(rows: list[tuple],
                      val_color: str = AppStyles.GREEN) -> QTableWidget:
        """Convenience: 3-column (Setting | Value | Note) table."""
        t = TableFactory.table(["Setting", "Value", "Note"], len(rows))
        for r, (name, val, note) in enumerate(rows):
            t.setItem(r, 0, TableFactory.cell(name))
            t.setItem(r, 1, TableFactory.cell(val, val_color, bold=True))
            t.setItem(r, 2, TableFactory.cell(note, AppStyles.MUTED))
        return t

class ResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._banner = self._make_banner()
        layout.addWidget(self._banner)
        self._pid_tab = PIDWidget()
        self._filter_tab = FilterWidget()

        tabs = QTabWidget()
        tabs.setStyleSheet(AppStyles.get_stylesheet())
        tabs.addTab(self._pid_tab, "PID Tuning")
        tabs.addTab(self._filter_tab, "Filter Settings")
        layout.addWidget(tabs)

    @staticmethod
    def _make_banner() -> QLabel:
        lbl = QLabel("  Load a log to see recommendations.")
        lbl.setStyleSheet(
            f"background:#1A1A1A; color:{AppStyles.MUTED}; font-family:Consolas;"
            "font-size:12px; padding:6px;"
        )
        return lbl

    def display_result(self, result: AnalysisResult):
        """Entry point called by MainWindow after every successful analysis."""
        self._update_banner(result)
        self._pid_tab.refresh(result)
        if result.filter_recommendation:
            self._filter_tab.refresh(result.filter_recommendation)

    def clear(self):
        self._banner.setText("  Load a log to see recommendations.")
        self._banner.setStyleSheet(
            f"background:#1A1A1A; color:{AppStyles.MUTED}; font-family:Consolas;"
            "font-size:12px; padding:6px;"
        )

    def _update_banner(self, result: AnalysisResult):
        score = result.overall_quality_score
        color = (AppStyles.GREEN if score >= 80 else
                 AppStyles.AMBER if score >= 60 else AppStyles.RED)
        self._banner.setText(
            f"  Score: {score:.0f}/100   │   {result.overall_assessment}"
        )
        self._banner.setStyleSheet(
            f"background:#1A1A1A; color:{color}; font-family:Consolas;"
            "font-size:12px; font-weight:bold; padding:6px;"
        )