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
        for ax in [self.ax_top, self.ax_bottom]:
            ax.set_facecolor(AppStyles.BG_PLOT)
            ax.tick_params(colors=AppStyles.TEXT)
            ax.xaxis.label.set_color(AppStyles.TEXT)
            ax.yaxis.label.set_color(AppStyles.TEXT)
            ax.title.set_color(AppStyles.TEXT)
            for spine in ax.spines.values():
                spine.set_color(AppStyles.BORDER)

    def clear_and_restyle(self):
        pass