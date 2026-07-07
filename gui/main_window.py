from PyQt5.QtWidgets import QMainWindow
from core.log_parser import LogParser
from core.tuning_engine import TuningEngine

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
        pass

    def _connect_signals(self):
        pass