import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from gui.style import AppStyles
from core.models.analysis import AnalysisResult

class FFTCanvas(FigureCanvasQTAgg):
    """
    FFT spectrum canvas — PID Toolbox style:
      - filled area under the spectrum curve
      - horizontal noise threshold line
      - text annotations for top 1-2 dominant peaks (no vertical lines)
    """

    MAX_FREQ_HZ  = 600.0
    MAX_PEAKS    = 2      # annotate at most 2 peaks
    MIN_PEAK_GAP = 30.0   # Hz — skip peaks closer than this

    def __init__(self):
        self._fig = Figure(facecolor=AppStyles.BG_DARK, constrained_layout=True)
        self._ax  = self._fig.add_subplot(111)
        super().__init__(self._fig)
        self._apply_style()

    def _apply_style(self):
        self._ax.set_facecolor(AppStyles.BG_PLOT)
        self._ax.tick_params(colors=AppStyles.TEXT)
        self._ax.xaxis.label.set_color(AppStyles.TEXT)
        self._ax.yaxis.label.set_color(AppStyles.TEXT)
        self._ax.title.set_color(AppStyles.TEXT)
        for spine in self._ax.spines.values():
            spine.set_color(AppStyles.BORDER)

    def render(self, axis_name: str, gyro: np.ndarray,
               sample_rate: float, peak_freqs: list):
        self._ax.clear()
        self._apply_style()

        freqs, amplitudes = self._compute_spectrum(gyro, sample_rate)
        threshold = self._noise_threshold(amplitudes)

        self._draw_filled_spectrum(freqs, amplitudes, threshold)
        self._draw_threshold_line(threshold)

        selected = self._select_peaks(peak_freqs, freqs, amplitudes, threshold)
        self._annotate_peaks(freqs, amplitudes, selected)
        self._set_labels(axis_name)
        self.draw()

    def _compute_spectrum(self, gyro: np.ndarray,
                          sample_rate: float) -> tuple[np.ndarray, np.ndarray]:
        n     = len(gyro)
        fft   = np.abs(np.fft.rfft(gyro * np.hanning(n))) / (n / 2)
        freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
        mask  = freqs <= self.MAX_FREQ_HZ
        return freqs[mask], fft[mask]

    @staticmethod
    def _noise_threshold(amplitudes: np.ndarray) -> float:
        """Mean + 2σ — marks clear outliers as noise peaks."""
        return float(np.mean(amplitudes) + 2 * np.std(amplitudes))

    def _draw_filled_spectrum(self, freqs: np.ndarray,
                              amplitudes: np.ndarray, threshold: float):
        """
        Draws the spectrum as a filled area:
          - below threshold: amber (normal noise floor)
          - above threshold: red (significant noise peaks)
        """
        # Base fill — entire spectrum in amber
        self._ax.fill_between(freqs, 0, amplitudes,
                              color=AppStyles.AMBER, alpha=0.35)
        self._ax.plot(freqs, amplitudes,
                      color=AppStyles.AMBER, linewidth=0.8, alpha=0.9)

        # Overlay red fill for values above threshold
        above = np.where(amplitudes > threshold, amplitudes, threshold)
        self._ax.fill_between(freqs, threshold, above,
                              where=(amplitudes > threshold),
                              color=AppStyles.RED, alpha=0.55)

    def _draw_threshold_line(self, threshold: float):
        self._ax.axhline(
            threshold,
            color=AppStyles.RED, linewidth=1.0,
            linestyle="--", alpha=0.6,
            label=f"Noise floor +2σ  ({threshold:.3f})"
        )

    def _annotate_peaks(self, freqs: np.ndarray,
                        amplitudes: np.ndarray, peak_freqs: list):
        """
        Adds a text annotation with an arrow for each selected peak.
        No vertical lines — just a label above the peak.
        """
        colors = [AppStyles.RED, AppStyles.CYAN]

        for i, pf in enumerate(peak_freqs):
            # Find the nearest frequency bin
            idx = int(np.argmin(np.abs(freqs - pf)))
            amp = float(amplitudes[idx])
            color = colors[i % len(colors)]

            self._ax.annotate(
                f"{pf:.0f} Hz",
                xy=(freqs[idx], amp),
                xytext=(freqs[idx], amp * 1.35 + 0.01),
                color=color,
                fontsize=9,
                fontweight="bold",
                ha="center",
                arrowprops=dict(
                    arrowstyle="->",
                    color=color,
                    lw=1.2,
                ),
            )

        if peak_freqs:
            self._ax.legend(
                facecolor=AppStyles.BG_WIDGET,
                edgecolor=AppStyles.BORDER,
                labelcolor=AppStyles.TEXT,
                fontsize=9,
            )

    def _select_peaks(self, peak_freqs: list, freqs: np.ndarray,
                  amplitudes: np.ndarray, threshold: float) -> list:
        """
        From the full list (sorted by amplitude, largest first),
        selects at most MAX_PEAKS peaks that are MIN_PEAK_GAP Hz apart.
        """
        selected = []
        for freq in peak_freqs:
            idx = int(np.argmin(np.abs(freqs - freq)))
            amp = float(amplitudes[idx])
            if amp < threshold * 2.0:
                continue
            if all(abs(freq - s) >= self.MIN_PEAK_GAP for s in selected):
                selected.append(freq)
            if len(selected) >= self.MAX_PEAKS:
                break
        return selected

    def _set_labels(self, axis_name: str):
        self._ax.set_title(f"{axis_name} — Gyro Noise Spectrum")
        self._ax.set_xlabel("Frequency (Hz)")
        self._ax.set_ylabel("Amplitude (deg/s)")
        self._ax.grid(True, color=AppStyles.BORDER, linestyle=":", alpha=0.4)


class FFTPlotWidget(QWidget):
    """Tab container with one FFTCanvas per axis (Roll / Pitch / Yaw)."""

    AXES = ["Roll", "Pitch", "Yaw"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canvases: dict[str, FFTCanvas] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        tabs   = QTabWidget()
        for axis in self.AXES:
            canvas = FFTCanvas()
            self._canvases[axis] = canvas
            tabs.addTab(canvas, axis)
        layout.addWidget(tabs)

    def plot_all(self, result: AnalysisResult):
        gyro_map = {
            "Roll":  result.flight_data.gyro_roll,
            "Pitch": result.flight_data.gyro_pitch,
            "Yaw":   result.flight_data.gyro_yaw,
        }
        for axis in self.AXES:
            fm    = result.filter_metrics.get(axis)
            peaks = fm.peak_frequencies if fm else []
            self._canvases[axis].render(
                axis, gyro_map[axis],
                result.flight_data.sample_rate_hz,
                peaks,
            )