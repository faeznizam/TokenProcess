import sys

from PyQt5.QtWidgets import QApplication
from ui.ui_file import MyApp



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())