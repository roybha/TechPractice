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

DARK_THEME = """
    QMainWindow { background-color: #121212; }
    QLabel { color: #E0E0E0; font-family: 'Segoe UI'; font-weight: bold; }
    QGroupBox { color: #888888; border: 1px solid #333333; margin-top: 10px; padding-top: 15px; font-weight: bold; }
    QSpinBox, QDoubleSpinBox { background-color: #1E1E1E; color: #FFFFFF; border: 1px solid #444444; padding: 5px; font-size: 14px; }
    QPushButton#actionButton { background-color: #1E1E1E; color: #00FF41; border: 2px solid #00FF41; padding: 15px; font-weight: bold; font-size: 14px; }
    QPushButton#actionButton:hover { background-color: #00FF41; color: #000000; }
    QLabel#statusLabel { color: #00FF41; font-family: 'Courier New'; font-size: 18px; font-weight: bold; padding: 10px; border: 1px solid #00FF41; background-color: #0A0A0A; }
    QTextEdit#consoleOutput { background-color: #050505; color: #00FF41; font-family: 'Consolas', monospace; font-size: 14px; border: 1px solid #333333; padding: 10px; }
    """