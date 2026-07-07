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
        group_layout = QVBoxLayout()

        # Weight
        group_layout.addWidget(QLabel("Weight (grams):"))
        self.weight_input = QSpinBox()
        self.weight_input.setRange(100, 20000)
        self.weight_input.setValue(1500)
        self.weight_input.setSingleStep(50)
        group_layout.addWidget(self.weight_input)

        # Prop size
        group_layout.addWidget(QLabel("Propeller Size (inches):"))
        self.prop_input = QDoubleSpinBox()
        self.prop_input.setRange(2.0, 20.0)
        self.prop_input.setValue(7.5)
        self.prop_input.setSingleStep(0.5)
        group_layout.addWidget(self.prop_input)

        # Motor KV
        group_layout.addWidget(QLabel("Motor KV:"))
        self.kv_input = QSpinBox()
        self.kv_input.setRange(200, 4000)
        self.kv_input.setValue(1300)
        self.kv_input.setSingleStep(50)
        group_layout.addWidget(self.kv_input)

        group.setLayout(group_layout)
        layout.addWidget(group)

        self.load_button = QPushButton("LOAD LOG (.CSV)")
        self.load_btn.setObjectName("actionButton")
        layout.addWidget(self.load_btn)

        layout.addStretch()



    def get_profile(self):
        return DroneProfile(
            weight_grams=self.weight_input.value(),
            prop_size_inches=self.prop_size_input.value(),
            motor_kv=self.motor_kv_input.value(),
        )