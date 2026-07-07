from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSplitter
from core.log_parser import LogParser
from core.tuning_engine import TuningEngine
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
        self.plot_widget = None
        self.console_widget = None
        splitter.addWidget(self.plot_widget)
        splitter.addWidget(self.console_widget)
        splitter.setSizes([560, 280])
        right_layout.addWidget(splitter)

        root_layout.addWidget(right_layout_widget,stretch=3)

    def _connect_signals(self):
        self.profile_widget.load_btn.clicked.connect()
        pass

    def _on_load_clicked(self):
        pass
    def _set_status(self, tex: str, color: str):
        pass