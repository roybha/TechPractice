from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from gui.style import AppStyles


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(facecolor=AppStyles.BG_DARK)
        self.ax = self.fig.add_subplot(211)
        self.ax_bottom = self.fig.add_subplot(212)
        self.fig.subplots_adjust(hspace=0.45)
        super().__init__(self.fig)

    def _style_axes(self):
        pass

    def clear_and_restyle(self):
        pass