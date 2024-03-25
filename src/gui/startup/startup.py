from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel
from PySide6.QtGui import QFont

from config.properties import APPLICATION_NAME


class QStartupWidget(QWidget):
    def __init__(self, set_step: Callable, run_step: Callable):
        super().__init__()
        self.layout = QVBoxLayout(self)
        v_margin = self.window().geometry().height() * 0.3
        h_margin = self.window().geometry().width() * 0.5
        self.layout.setContentsMargins(h_margin, v_margin, h_margin, v_margin)

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(32)
        self.title = QLabel(APPLICATION_NAME)
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setFont(title_font)
        self.set_btn = QPushButton('setting')
        self.run_btn = QPushButton('run')
        self.set_btn.clicked.connect(set_step)
        self.run_btn.clicked.connect(run_step)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.set_btn)
        self.layout.addWidget(self.run_btn)

