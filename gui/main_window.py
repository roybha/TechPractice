from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSplitter, QFileDialog, QApplication
from core.log_parser import LogParser
from core.tuning_engine import TuningEngine
from gui.style import AppStyles
from gui.widgets.console_widget import ConsoleWidget
from gui.widgets.plot_widget import PlotWidget
from gui.widgets.profile_widget import ProfileWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PID Analyzer")
        self.setGeometry(100, 100, 1400, 860)
        self.setMinimumSize(1100, 700)

        self._parser = LogParser()
        self._engine = TuningEngine()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        # Left panel
        self.profile_widget = ProfileWidget()
        root_layout.addWidget(self.profile_widget, stretch=1)

        # Right panel
        right_layout_widget = QWidget()
        right_layout = QVBoxLayout(right_layout_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Status raw above
        self.status_label = QLabel("SYSTEM STANDBY")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.status_label)

        # Splitter: plots above, console below
        splitter = QSplitter(Qt.Vertical)
        self.plot_widget = PlotWidget()
        self.console_widget = ConsoleWidget()
        splitter.addWidget(self.plot_widget)
        splitter.addWidget(self.console_widget)
        splitter.setSizes([560, 280])
        right_layout.addWidget(splitter)

        root_layout.addWidget(right_layout_widget,stretch=3)

    def _connect_signals(self):
        self.profile_widget.load_button.clicked.connect(self._on_load_clicked)

    def _on_load_clicked(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Blackbox Log", "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not filepath:
            return

        self._set_status("ANALYZING...", AppStyles.AMBER)
        self.console_widget.clear()
        self.console_widget.log(f"[SYSTEM] Loading: {filepath}")
        QApplication.processEvents()

        try:
            profile = self.profile_widget.get_profile()
            flight_data = self._parser.parse(filepath)
            result = self._engine.analyze(flight_data, profile)

            self.plot_widget.plot_all(flight_data)
            self.console_widget.display_result(result)

            self._set_status("ANALYSIS COMPLETE", AppStyles.GREEN)

        except FileNotFoundError as e:
            self._handle_error(f"File not found: {e}")
        except ValueError as e:
            self._handle_error(f"Parse error: {e}")
        except Exception as e:
            self._handle_error(f"Unexpected error: {e}")

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color}; border-color: {color};"
        )

    def _handle_error(self, message: str):
        self.console_widget.log(f"\n[ERROR] {message}")
        self._set_status("ANALYSIS FAILED", AppStyles.RED)