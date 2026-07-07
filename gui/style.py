class AppStyles:

    BG_DARK    = "#121212"
    BG_WIDGET  = "#1E1E1E"
    BG_PLOT    = "#050505"
    GREEN      = "#00FF41"   # active elements
    AMBER      = "#FFB000"   #  actual plot
    RED        = "#FF003C"   # error plot
    TEXT       = "#E0E0E0"
    BORDER     = "#333333"

    @staticmethod
    def get_stylesheet() -> str:
        return DARK_THEME

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