from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem
from gui.style import AppStyles
from core.models.recommendations import FilterRecommendation
from results_widget import TableFactory

class FilterWidget(QWidget):
    """
        Displays filter recommendations as numbered sections:
          ① RPM Filter
          ② Dynamic Notch
          ③ Gyro Lowpass
          ④ Static Notch  (only when strong peaks detected)
          ⑤ D-Term & Yaw Lowpass
        """

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{AppStyles.BG};")
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(6)

    def refresh(self, fr: FilterRecommendation):
        self._clear()
        self._add_rpm(fr)
        self._add_dynamic_notch(fr)
        self._add_gyro_lpf(fr)
        self._add_static_notch(fr)
        self._add_dterm_yaw(fr)
        self._layout.addStretch()

    def _add_rpm(self, fr: FilterRecommendation):
        self._layout.addWidget(TableFactory.section_label(
            "① RPM Filter  —  enable first, most effective"))
        self._layout.addWidget(TableFactory.setting_table([
            ("Harmonics", str(fr.rpm_filter_harmonics),
             "covers fundamental + 2 harmonics"),
            ("Min Frequency", f"{fr.rpm_filter_min_hz:.0f} Hz",
             "multiply ×1.5 for 6S battery"),
        ]))

    def _add_dynamic_notch(self, fr: FilterRecommendation):
        self._layout.addWidget(TableFactory.section_label(
            "② Dynamic Notch Filter"))
        self._layout.addWidget(TableFactory.setting_table([
            ("Width Percent", f"{fr.dyn_notch_width_pct} %", "8% = good default"),
            ("Q", str(fr.dyn_notch_q), "250=wide  350=narrow"),
            ("Min Hz", f"{fr.dyn_notch_min_hz:.0f} Hz", "lower search bound"),
            ("Max Hz", f"{fr.dyn_notch_max_hz:.0f} Hz", "upper search bound"),
        ]))

    def _add_gyro_lpf(self, fr: FilterRecommendation):
        self._layout.addWidget(TableFactory.section_label(
            "③ Gyro Lowpass (Dynamic)"))
        self._layout.addWidget(TableFactory.setting_table([
            ("LPF1 Dynamic Min", f"{fr.gyro_lpf_min_hz:.0f} Hz",
             "lower bound of dynamic range"),
            ("LPF1 Dynamic Max", f"{fr.gyro_lpf_max_hz:.0f} Hz",
             "upper bound of dynamic range"),
        ]))

    def _add_static_notch(self, fr: FilterRecommendation):
        if fr.gyro_notch1_center_hz == 0:
            return
        self._layout.addWidget(TableFactory.section_label(
            "④ Gyro Static Notch  —  use only if RPM+DynNotch insufficient"))
        rows = [
            ("Notch 1 Center", f"{fr.gyro_notch1_center_hz:.0f} Hz", "strongest peak"),
            ("Notch 1 Cutoff", f"{fr.gyro_notch1_cutoff_hz:.0f} Hz", "85% of center"),
        ]
        if fr.gyro_notch2_center_hz > 0:
            rows += [
                ("Notch 2 Center", f"{fr.gyro_notch2_center_hz:.0f} Hz", "second peak"),
                ("Notch 2 Cutoff", f"{fr.gyro_notch2_cutoff_hz:.0f} Hz", "85% of center"),
            ]
        self._layout.addWidget(
            TableFactory.setting_table(rows, val_color= AppStyles.AMBER))

    def _add_dterm_yaw(self, fr: FilterRecommendation):
        self._layout.addWidget(TableFactory.section_label(
            "⑤ D-Term & Yaw Lowpass"))
        self._layout.addWidget(TableFactory.setting_table([
            ("D-Term LPF1 Min", f"{fr.dterm_lpf1_min_hz:.0f} Hz", "dynamic lower bound"),
            ("D-Term LPF1 Max", f"{fr.dterm_lpf1_max_hz:.0f} Hz", "dynamic upper bound"),
            ("D-Term LPF2", f"{fr.dterm_lpf2_hz:.0f} Hz", "static cutoff"),
            ("Yaw LPF Cutoff", f"{fr.yaw_lpf_hz:.0f} Hz", "yaw axis filter"),
        ]))

    def _clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()