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
        pass