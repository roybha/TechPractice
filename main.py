import sys
import matplotlib
from gui.main_window import MainWindow
from gui.style import AppStyles

matplotlib.use('QT5Agg')

from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(AppStyles.get_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()