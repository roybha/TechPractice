from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTabWidget, QSplitter, QFileDialog, QApplication,
)
from core.log_parser import LogParser
from core.tuning_engine import TuningEngine
from core.models.analysis import AnalysisResult
from gui.style import AppStyles
from gui.widgets.profile_widget import ProfileWidget
from gui.widgets.plot_widget import PlotWidget
from gui.widgets.fft_plot_widget import FFTPlotWidget
from gui.widgets.results_widget import ResultsWidget
from database.db_manager import DBManager

class MainWindow(QMainWindow):
    """
    Top-level window. Responsibility: layout assembly and event routing.
    Business logic lives in core; visual logic lives in widgets.

    Layout:
      Left  — ProfileWidget (drone config + load button)
      Right — status banner
              ├── graph tabs : Step Response | Noise/FFT
              └── result tabs: PID Tuning   | Filter Settings
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PID Analyzer")
        self.showMaximized()
        self.setMinimumSize(1100, 700)

        self._parser = LogParser()
        self._engine = TuningEngine()
        self._db = DBManager()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)
        root.addWidget(self._build_left_panel(),  stretch=1)
        root.addWidget(self._build_right_panel(), stretch=3)

    def _build_left_panel(self) -> QWidget:
        """Drone config form and load button."""
        self.profile_widget = ProfileWidget()
        return self.profile_widget

    def _build_right_panel(self) -> QWidget:
        """Status banner + vertical splitter (graphs top, tables bottom)."""
        panel  = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._build_status_label())
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self._build_graph_tabs())
        splitter.addWidget(self._build_results_area())
        splitter.setSizes([480, 360])
        layout.addWidget(splitter)
        return panel

    def _build_status_label(self) -> QLabel:
        self.status_label = QLabel("SYSTEM STANDBY")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        return self.status_label

    def _build_graph_tabs(self) -> QTabWidget:
        """Step Response graph and Noise/FFT spectrum."""
        tabs = QTabWidget()
        tabs.setStyleSheet(AppStyles.tab_style())   # ← uses shared style
        self.plot_widget     = PlotWidget()
        self.fft_plot_widget = FFTPlotWidget()
        tabs.addTab(self.plot_widget,     "Step Response")
        tabs.addTab(self.fft_plot_widget, "Noise / FFT")
        return tabs

    def _build_results_area(self) -> ResultsWidget:
        """PID and Filter recommendation tables."""
        self.results_widget = ResultsWidget()
        return self.results_widget

    def _connect_signals(self):
        self.profile_widget.load_button.clicked.connect(self._on_load_clicked)

    def _on_load_clicked(self):
        filepath = self._open_file_dialog()
        if not filepath:
            return

        self._set_status("ANALYZING...", AppStyles.AMBER)
        self.results_widget.clear()
        QApplication.processEvents()

        try:
            result = self._run_analysis(filepath)
            self._display_result(result)
            profile = self.profile_widget.get_profile()
            session_id = self._db.save_analysis(result, profile)
            self._set_status(
                f"ANALYSIS COMPLETE  —  Score: {result.overall_quality_score:.0f}/100 | Saved DB ID: {session_id}",
                AppStyles.GREEN,
            )
        except FileNotFoundError as e:
            self._handle_error(f"File not found: {e}")
        except ValueError as e:
            self._handle_error(f"Parse error: {e}")
        except Exception as e:
            self._handle_error(f"Unexpected error: {e}")

    def _open_file_dialog(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Blackbox Log", "",
            "CSV Files (*.csv);;All Files (*)",
        )
        return path

    def _run_analysis(self, filepath: str) -> AnalysisResult:
        profile     = self.profile_widget.get_profile()
        flight_data = self._parser.parse(filepath)
        return self._engine.analyze(flight_data, profile)

    def _display_result(self, result: AnalysisResult):
        self.plot_widget.plot_all(result.flight_data)
        self.fft_plot_widget.plot_all(result)
        self.results_widget.display_result(result)

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color:{color}; border-color:{color};")

    def _handle_error(self, message: str):
        self._set_status(f"ERROR: {message}", AppStyles.RED)