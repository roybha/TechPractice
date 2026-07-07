from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QSpinBox, QDoubleSpinBox, QPushButton
from core.models.drone_profile import DroneProfile

class ProfileWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.weight_input: QSpinBox = None
        self.prop_input: QDoubleSpinBox = None
        self.kv_input: QSpinBox = None
        self.load_button: QPushButton = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        group = QGroupBox("DRONE CONFIGURATION")

    def get_profile(self):
        return DroneProfile(
            weight_grams=self.weight_input.value(),
            prop_size_inches=self.prop_size_input.value(),
            motor_kv=self.motor_kv_input.value(),
        )