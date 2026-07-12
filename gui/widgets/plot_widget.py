import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from gui.style import AppStyles
from gui.widgets.matplotlib_canvas import MplCanvas


class PlotWidget(QWidget):
    AXES = ['Roll', 'Pitch', 'Yaw']

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canvases: dict[str, MplCanvas] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setObjectName('plotTabs')

        for axis in self.AXES:
            canvas = MplCanvas()
            self._canvases[axis] = canvas
            self.tabs.addTab(canvas, axis)
        layout.addWidget(self.tabs)

    def plot_axis(self,
                  axis_name: str,
                  timestamp_us: np.ndarray,
                  setpoint: np.ndarray,
                  gyro: np.ndarray):

        canvas = self._canvases[axis_name]
        canvas.clear_and_restyle()

        time = timestamp_us / 1_000_000.0

        # Upper command/reaction
        canvas.ax_top.plot(time, setpoint, label='Setpoint',
                           color=AppStyles.GREEN, linestyle='--', linewidth=1.5)
        canvas.ax_top.plot(time, gyro, label='Gyro (Actual)',
                           color=AppStyles.AMBER, alpha=0.85, linewidth=1.5)
        canvas.ax_top.set_title(f"{axis_name} — Kinematic Response")
        canvas.ax_top.set_ylabel("deg/s")
        canvas.ax_top.legend(facecolor=AppStyles.BG_WIDGET,
                             edgecolor=AppStyles.BORDER,
                             labelcolor=AppStyles.TEXT)
        canvas.ax_top.grid(True, color=AppStyles.BORDER, linestyle=":", alpha=0.6)

        # Lower PID error
        error = gyro - setpoint
        canvas.ax_bottom.plot(time, error, label="Tracking Error - Setpoint - Gyro",
                              color=AppStyles.RED, linewidth=1.2)
        canvas.ax_bottom.set_title(f"{axis_name} — PID Error")
        canvas.ax_bottom.set_xlabel("Time (s)")
        canvas.ax_bottom.set_ylabel("Deviation (deg/s)")
        canvas.ax_bottom.axhline(0, color=AppStyles.BORDER, linewidth=0.8)
        canvas.ax_bottom.legend(facecolor=AppStyles.BG_WIDGET,
                                edgecolor=AppStyles.BORDER,
                                labelcolor=AppStyles.TEXT)
        canvas.ax_bottom.grid(True, color=AppStyles.BORDER, linestyle=":", alpha=0.6)

        canvas.draw()

    def plot_all(self, flight_data):
        self.plot_axis("Roll", flight_data.timestamp,
                       flight_data.setpoint_roll, flight_data.gyro_roll)
        self.plot_axis("Pitch", flight_data.timestamp,
                       flight_data.setpoint_pitch, flight_data.gyro_pitch)
        self.plot_axis("Yaw", flight_data.timestamp,
                       flight_data.setpoint_yaw, flight_data.gyro_yaw)