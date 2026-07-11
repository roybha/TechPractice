from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSplitter, QFileDialog, QApplication
from core.log_parser import LogParser
from core.tuning_engine import TuningEngine
from gui.style import AppStyles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PID Analyzer")
        self.setGeometry(100, 100, 1440, 900)
        self.setMinimumSize(1100, 700)

        self._parser = LogParser()
        self._engine = TuningEngine()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        root.addWidget(self._build_left_panel(), stretch=1)
        root.addWidget(self._build_right_panel(), stretch=3)

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
            self._set_status(
                f"ANALYSIS COMPLETE  —  Score: {result.overall_quality_score:.0f}/100",
                AppStyles.GREEN,
            )
        except FileNotFoundError as e:
            self._handle_error(f"File not found: {e}")
        except ValueError as e:
            self._handle_error(f"Parse error: {e}")
        except Exception as e:
            self._handle_error(f"Unexpected error: {e}")

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color:{color}; border-color:{color};"
        )

    def _handle_error(self, message: str):
        self._set_status(f"ERROR: {message}", AppStyles.RED)