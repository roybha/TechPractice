import numpy as np
from scipy.signal import find_peaks
from core.models import FilterMetrics

class FFTAnalyzer:

    def analyze_axis(self, axis_name: str, gyro_data: np.ndarray, sample_rate_hz: float) -> FilterMetrics:
        # 1: smoothing
        windowed_gyro_data = self._apply_window(gyro_data)

        #  2: Fourier transform
        frequencies, amplitudes = self._compute_fft(windowed_gyro_data, sample_rate_hz)

        # 3: peak search
        peak_freqs, peak_amps = self._find_noise_peaks(frequencies, amplitudes)

        # 4: analysis of results and data preparation
        dominant_freq = 0.0
        dominant_amp = 0.0
        lpf_cutoff = 0.0
        notch_freq = 0.0

        # if the algorithm found at least one noise
        if len(peak_freqs) > 0:
            dominant_freq = peak_freqs[0]  # take the first one because we sorted them out
            dominant_amp = peak_amps[0]

            notch_freq = dominant_freq
            lpf_cutoff = dominant_freq * 0.7  # basic cutoff formula for LPF

        # 5: packaging and return of DTO
        return FilterMetrics(
            axis_name=axis_name,
            dominant_noise_frequency=dominant_freq,
            noise_amplitude=dominant_amp,
            peak_frequencies=peak_freqs,
            peak_amplitudes=peak_amps,
            recommended_lpf_cutoff_frequency=lpf_cutoff,
            recommended_notch_frequency=notch_freq
        )

    @staticmethod
    def _apply_window(gyro_data: np.ndarray) -> np.ndarray:
        length = len(gyro_data)

        # creating Hann window, which smoothly reduces the edges of the array to zero
        hann_window = np.hanning(length)

        # multiply the raw gyroscope data by the window, leaving the center unchanged
        # and "smoothing" the edges of the graph.
        return gyro_data * hann_window

    @staticmethod
    def _compute_fft(windowed_data: np.ndarray, sampling_rate: float):
        length = len(windowed_data)
        # perform Real FFT (rfft). Standard FFT calculates negative frequencies for complex signals.
        # Since our gyro readings are purely real values, rfft is faster and only computes
        # the positive frequencies we actually need.
        complex_array = np.fft.rfft(windowed_data)

        # extract absolute amplitude and normalize it to real physical degrees/sec
        amplitudes = np.abs(complex_array) / (length / 2)

        # generate X-axis (frequencies in Hz) up to the Nyquist limit.
        # d is the time step between samples
        frequencies = np.fft.rfftfreq(length, d=1 / sampling_rate)

        return frequencies, amplitudes

    @staticmethod
    def _find_noise_peaks(frequencies: np.ndarray, amplitudes: np.ndarray):
        # cut off the useful control signal (everything below 20 Hz)
        mask = frequencies >= 20.0
        filtered_frequencies = frequencies[mask]
        filtered_amplitudes = amplitudes[mask]

        # setting a dynamic noise threshold
        noise_threshold = np.mean(filtered_amplitudes) + np.std(filtered_amplitudes)
        # find the INDEXES of the peaks (take only the first element from the tuple)
        peaks_indexes, _ = find_peaks(filtered_amplitudes, height=noise_threshold)

        # extract specific values of frequencies and amplitudes from the found indices
        peak_freqs = filtered_frequencies[peaks_indexes]
        peak_amps = filtered_amplitudes[peaks_indexes]

        # synchronous sorting:
        # argsort returns indices from smallest amplitude to largest.
        # [::-1] reverses this list so that the largest amplitude is first.
        sort_order = np.argsort(peak_amps)[::-1]

        # apply this order to both arrays and convert them into regular lists (list)
        sorted_freqs = peak_freqs[sort_order].tolist()
        sorted_amps = peak_amps[sort_order].tolist()

        return sorted_freqs, sorted_amps