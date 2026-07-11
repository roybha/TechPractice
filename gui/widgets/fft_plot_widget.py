import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from gui.style import AppStyles
from core.models.analysis import AnalysisResult
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

class FFTCanvas(FigureCanvasQTAgg):
    """
    Single matplotlib canvas for one gyro axis FFT spectrum.
    Responsibility: draw and style one frequency-domain plot.
    """

    MAX_FREQ_HZ = 600.0  # display range cap

    def __init__(self):
        self._fig = Figure(facecolor=AppStyles.BG_DARK)
        self._ax = self._fig.add_subplot(111)
        super().__init__(self._fig)
        self._apply_style()

    # Style
    def _apply_style(self):
        self._ax.set_facecolor(AppStyles.BG_PLOT)
        self._ax.tick_params(colors=AppStyles.TEXT)
        self._ax.xaxis.label.set_color(AppStyles.TEXT)
        self._ax.yaxis.label.set_color(AppStyles.TEXT)
        self._ax.title.set_color(AppStyles.TEXT)
        for spine in self._ax.spines.values():
            spine.set_color(AppStyles.BORDER)

    # Public
    def render(self, axis_name: str, gyro: np.ndarray,
               sample_rate: float, peak_freqs: list):
        """Redraws the spectrum. Call after each new analysis."""
        self._ax.clear()
        self._apply_style()
        self._draw_spectrum(gyro, sample_rate)
        self._mark_peaks(peak_freqs)
        self._set_labels(axis_name)
        self._fig.tight_layout()
        self.draw()

    # Private
    def _draw_spectrum(self, gyro: np.ndarray, sample_rate: float):
        n = len(gyro)
        fft = np.abs(np.fft.rfft(gyro * np.hanning(n))) / (n / 2)
        freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)

        mask = freqs <= self.MAX_FREQ_HZ
        self._ax.plot(freqs[mask], fft[mask],
                      color=AppStyles.AMBER, linewidth=0.8, alpha=0.9)

    def _mark_peaks(self, peak_freqs: list):
        for freq in peak_freqs:
            self._ax.axvline(freq, color=AppStyles.RED, linewidth=1.2,
                             linestyle="--", alpha=0.75, label=f"{freq:.0f} Hz")
        if peak_freqs:
            self._ax.legend(facecolor=AppStyles.BG_WIDGET,
                            edgecolor=AppStyles.BORDER,
                            labelcolor=AppStyles.TEXT, fontsize=9)

    def _set_labels(self, axis_name: str):
        self._ax.set_title(f"{axis_name} — Gyro Noise Spectrum")
        self._ax.set_xlabel("Frequency (Hz)")
        self._ax.set_ylabel("Amplitude (deg/s)")
        self._ax.grid(True, color=AppStyles.BORDER, linestyle=":", alpha=0.5)

class FFTPlotWidget(QWidget):
    """
    Tab container with one FFTCanvas per axis (Roll / Pitch / Yaw).
    Responsibility: layout management and routing data to correct canvas.
    """

    AXES = ["Roll", "Pitch", "Yaw"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canvases: dict[str, FFTCanvas] = {}
        self._build_ui()

    # Build
    def _build_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        for axis in self.AXES:
            canvas = FFTCanvas()
            self._canvases[axis] = canvas
            tabs.addTab(canvas, axis)

        layout.addWidget(tabs)

    # Public
    def plot_all(self, result: AnalysisResult):
        """Renders FFT spectrum for every axis from AnalysisResult."""
        gyro_map = {
            "Roll": result.flight_data.gyro_roll,
            "Pitch": result.flight_data.gyro_pitch,
            "Yaw": result.flight_data.gyro_yaw,
        }
        for axis in self.AXES:
            fm = result.filter_metrics.get(axis)
            peaks = fm.peak_frequencies if fm else []
            self._canvases[axis].render(
                axis, gyro_map[axis],
                result.flight_data.sample_rate_hz,
                peaks,
            )