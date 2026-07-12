from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QAbstractScrollArea,
)

from gui.style import AppStyles


class TableFactory:
    """Static factory for styled table cells, tables and section labels."""

    @staticmethod
    def cell(text: str, color: str = AppStyles.TEXT,
             bold: bool = False) -> QTableWidgetItem:
        it = QTableWidgetItem(str(text))
        it.setForeground(QColor(color))
        it.setFlags(Qt.ItemIsEnabled)
        if bold:
            f = QFont("Consolas", 11)
            f.setBold(True)
            it.setFont(f)
        return it

    @staticmethod
    def table(headers: list[str], rows: int,
              row_h: int = 28) -> QTableWidget:
        t = QTableWidget(rows, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionMode(QTableWidget.NoSelection)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setStyleSheet(AppStyles.table_style())

        # Size policy: table sizes to its content
        # setFixedHeight prevented scroll from working.
        # setSizeAdjustPolicy makes the table exactly as tall as its rows.
        t.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        t.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # outer scroll handles it
        t.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set uniform row heights
        for r in range(rows):
            t.setRowHeight(r, row_h)

        return t

    @staticmethod
    def section_label(text: str) -> QLabel:
        lbl = QLabel(f"  {text}")
        lbl.setStyleSheet(AppStyles.section_label_style())
        return lbl

    @staticmethod
    def setting_table(rows: list[tuple],
                      val_color: str = AppStyles.GREEN) -> QTableWidget:
        """3-column convenience table: Setting | Value | Note."""
        t = TableFactory.table(["Setting", "Value", "Note"], len(rows))
        for r, (name, val, note) in enumerate(rows):
            t.setItem(r, 0, TableFactory.cell(name))
            t.setItem(r, 1, TableFactory.cell(val, val_color, bold=True))
            t.setItem(r, 2, TableFactory.cell(note, AppStyles.MUTED))
        return t