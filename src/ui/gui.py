import sys

from PyQt5.QtWidgets import QApplication

from src.ui.components.MainWindow import MainWindow

class Application:
    def run(self):
        # Creat application instance
        app = QApplication(sys.argv)

        win = MainWindow()
        win.show()

        # Run loop
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = Application()
    app.run()