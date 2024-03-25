from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPalette, QColor, QFont, QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QPushButton

from config.paths import BTN_CLOSE_HOVER_IMG, BTN_CLOSE_NORMAL_IMG, ICON_IMG
from config.properties import APPLICATION_NAME

MAX_WIDTH = 720
MIN_WIDTH = 480


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        """ Set environ """

        """ Style setting """
        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.palette.setColor(QPalette.Window, QColor(72, 72, 72))
        self.setPalette(self.palette)

        """ Window setting """
        self.setWindowIcon(QIcon(ICON_IMG))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.title_bar = QTitleBar(self)
        self.layout().setMenuBar(self.title_bar)

        geometry = self.screen().availableGeometry()
        width = min(geometry.height(), geometry.width()) * 0.8
        width = max(width, MIN_WIDTH)
        width = min(width, MAX_WIDTH)
        height = width * 1.6
        self.setFixedSize(height, width)
        self.status = self.statusBar()

        self.setCentralWidget(widget)
        self.show()

    def _init_menu(self) -> None:
        pass


class QTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        """ Style setting """
        self.setFixedHeight(28)

        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.palette.setColor(QPalette.Window, QColor(27, 27, 27))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        """ Set title layout """
        self.title_layout = QHBoxLayout()
        self.title_layout.setContentsMargins(10, 0, 0, 0)

        title_font = QFont()
        title_font.setBold(True)
        title_label = QLabel(APPLICATION_NAME)
        title_label.setFont(title_font)

        self.title_layout.addWidget(title_label)

        """ Set toolbar layout """
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(30, 0, 30, 0)

        """ Set button layout """
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.button_layout.setContentsMargins(0, 0, 20, 0)

        close_button = QPushButton()
        close_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_CLOSE_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_CLOSE_HOVER_IMG}");
            }}
            '''
        )
        close_button.clicked.connect(self.window().close)

        self.button_layout.addWidget(close_button)

        """ Set main layout"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.title_layout, stretch=4)
        self.layout.addLayout(self.toolbar_layout, stretch=4)
        self.layout.addLayout(self.button_layout, stretch=1)

        # Variables for handling window dragging
        self.mouse_press_position = None
        self.window_position_on_press = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_position = event.globalPos()
            self.window_position_on_press = self.window().pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_press_position is not None:
            delta = event.globalPos() - self.mouse_press_position
            self.window().move(self.window_position_on_press + delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_position = None
            self.window_position_on_press = None
