from PyQt5.QtWidgets import QWidget

from gui.widgets.matplotlib_canvas import MplCanvas


class PlotWidget(QWidget):
    AXES = ['Roll', 'Pitch', 'Yaw']

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canvases: dict[str, MplCanvas] = {}
        self._build_ui()

    def _build_ui(self):
        pass

    def plot_axis(self, axis_name):
        pass

    def plot_all(self, flight_data):
        self.plot_axis('Roll')
        self.plot_axis('Pitch')
        self.plot_axis('Yaw')