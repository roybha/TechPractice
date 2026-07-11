class AppStyles:

    # Base palette
    BG_DARK    = "#121212"
    BG_WIDGET  = "#1E1E1E"
    BG_PLOT    = "#050505"
    BG_TABLE   = "#1A1A1A"  # table backgrounds
    BG_HEAD    = "#2A2A2A"  # table / tab headers

    # Accent colors
    GREEN      = "#00FF41"   # active elements
    AMBER      = "#FFB000"   #  actual plot
    RED        = "#FF003C"   # error plot
    CYAN       = "#00B4D8"  # axis labels, highlight
    TEXT       = "#E0E0E0"
    MUTED      = "#555555"  # secondary / disabled text
    BORDER     = "#333333"

    # QSS builders
    @staticmethod
    def get_stylesheet() -> str:
        return DARK_THEME

    @staticmethod
    def table_style() -> str:
        """QSS for QTableWidget — import once, reuse everywhere."""
        return f"""
                    QTableWidget {{
                        background: {AppStyles.BG_TABLE};
                        color: {AppStyles.TEXT};
                        font-family: Consolas;
                        font-size: 12px;
                        border: 1px solid {AppStyles.BORDER};
                        gridline-color: {AppStyles.BORDER};
                    }}
                    QHeaderView::section {{
                        background: {AppStyles.BG_HEAD};
                        color: {AppStyles.MUTED};
                        font-weight: bold;
                        padding: 4px;
                        border: none;
                    }}
                    QTableWidget::item {{ padding: 3px 6px; }}
                """

    @staticmethod
    def tab_style() -> str:
        """QSS for QTabWidget — consistent across all tab containers."""
        return f"""
                QTabWidget::pane {{
                    border: 1px solid {AppStyles.BORDER};
                    background: {AppStyles.BG_DARK};
                }}
                QTabBar::tab {{
                    background: {AppStyles.BG_WIDGET};
                    color: {AppStyles.MUTED};
                    padding: 6px 18px;
                    font-family: Consolas;
                    font-size: 12px;
                }}
                QTabBar::tab:selected {{
                    background: {AppStyles.BG_HEAD};
                    color: {AppStyles.GREEN};
                }}
            """

    @staticmethod
    def banner_style(color: str) -> str:
        """Inline style for the status/score banner label."""
        return (
            f"background: {AppStyles.BG_TABLE}; color: {color}; "
            "font-family: Consolas; font-size: 12px; "
            "font-weight: bold; padding: 6px;"
        )

    @staticmethod
    def section_label_style() -> str:
        """Inline style for green section headers inside result tabs."""
        return (
            f"background: #1C2B1C; color: {AppStyles.GREEN}; "
            "font-family: Consolas; font-size: 12px; "
            "font-weight: bold; padding: 5px; border-radius: 3px;"
        )


_DARK_THEME = f"""
    QMainWindow {{ background-color: {AppStyles.BG_DARK}; }}

    QLabel {{
        color: {AppStyles.TEXT};
        font-family: 'Segoe UI';
        font-weight: bold;
    }}

    QGroupBox {{
        color: #888888;
        border: 1px solid {AppStyles.BORDER};
        margin-top: 10px;
        padding-top: 15px;
        font-weight: bold;
    }}

    QSpinBox, QDoubleSpinBox {{
        background-color: {AppStyles.BG_WIDGET};
        color: #FFFFFF;
        border: 1px solid #444444;
        padding: 5px;
        font-size: 14px;
    }}

    QPushButton#actionButton {{
        background-color: {AppStyles.BG_WIDGET};
        color: {AppStyles.GREEN};
        border: 2px solid {AppStyles.GREEN};
        padding: 15px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton#actionButton:hover {{
        background-color: {AppStyles.GREEN};
        color: #000000;
    }}

    QLabel#statusLabel {{
        color: {AppStyles.GREEN};
        font-family: 'Courier New';
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
        border: 1px solid {AppStyles.GREEN};
        background-color: #0A0A0A;
    }}

    QTextEdit#consoleOutput {{
        background-color: {AppStyles.BG_PLOT};
        color: {AppStyles.GREEN};
        font-family: 'Consolas', monospace;
        font-size: 14px;
        border: 1px solid {AppStyles.BORDER};
        padding: 10px;
    }}

    QTableWidget {{
        background: {AppStyles.BG_TABLE};
        color: {AppStyles.TEXT};
        font-family: Consolas;
        font-size: 12px;
        border: 1px solid {AppStyles.BORDER};
        gridline-color: {AppStyles.BORDER};
    }}
    QHeaderView::section {{
        background: {AppStyles.BG_HEAD};
        color: {AppStyles.MUTED};
        font-weight: bold;
        padding: 4px;
        border: none;
    }}
    QTableWidget::item {{ padding: 3px 6px; }}

    QTabWidget::pane {{
        border: 1px solid {AppStyles.BORDER};
        background: {AppStyles.BG_DARK};
    }}
    QTabBar::tab {{
        background: {AppStyles.BG_WIDGET};
        color: {AppStyles.MUTED};
        padding: 6px 18px;
        font-family: Consolas;
        font-size: 12px;
    }}
    QTabBar::tab:selected {{
        background: {AppStyles.BG_HEAD};
        color: {AppStyles.GREEN};
    }}

    QScrollArea {{ border: none; background: {AppStyles.BG_DARK}; }}

    QSplitter::handle {{ background: {AppStyles.BORDER}; }}
"""