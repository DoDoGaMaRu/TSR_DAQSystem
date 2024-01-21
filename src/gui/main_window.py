from PySide6.QtWidgets import QMainWindow


MAX_WIDTH = 900
MIN_WIDTH = 480


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        # Environ Setting

        # Menu
        self._menu = self.menuBar()
        self._init_menu()

        # Window Setting
        geometry = self.screen().availableGeometry()

        width = min(geometry.height(), geometry.width()) * 0.6
        width = max(width, MIN_WIDTH)
        width = min(width, MAX_WIDTH)
        height = width * 1.6
        self.setFixedSize(height, width)
        self.status = self.statusBar()
        self.show()

        self.setCentralWidget(widget)

    def _init_menu(self):
        pass
