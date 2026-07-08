from cProfile import label

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from scipy.stats import alpha

from gui.style import AppStyles
from gui.widgets.matplotlib_canvas import MplCanvas


class PlotWidget(QWidget):
    AXES = ['Roll', 'Pitch', 'Yaw']

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canvases: dict[str, MplCanvas] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setObjectName('plotTabs')

        for axis in self.AXES:
            canvas = MplCanvas()
            self._canvases[axis] = canvas
            self.tabs.addTab(canvas, axis)

    def plot_axis(self,
                  axis_name: str,
                  timestamp_us: np.ndarray,
                  setpoint: np.ndarray,
                  gyro: np.ndarray):

        canvas = self._canvases[axis_name]
        canvas.clear_and_restyle()

        time = timestamp_us / 1_000_000.0

        # Upper
        canvas.ax_top.plot(time, setpoint, label='Setpoint',
                           color=AppStyles.GREEN, linestyle='--', linewidth=1.5)
        canvas.ax_top.plot(time, gyro, label='Gyro (Actual)',
                           color=AppStyles.AMBER, alpha=0.85, linewidth=1.5)
        canvas.ax_top.set_title(axis_name, f"{axis_name} — Kinematic Response")
        canvas.ax_top.set_ylabel("deg/s")
        canvas.ax_top.legend(facecolor=AppStyles.BG_WIDGET,
                             edgecolor=AppStyles.BORDER,
                             labelcolor=AppStyles.TEXT)
        canvas.ax_top.grid(True, color=AppStyles.BORDER, linestyle=":", alpha=0.6)


    def plot_all(self, flight_data):
        self.plot_axis('Roll')
        self.plot_axis('Pitch')
        self.plot_axis('Yaw')