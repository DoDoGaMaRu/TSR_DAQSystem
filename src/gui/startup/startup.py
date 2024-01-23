from typing import Callable

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class QStartupWidget(QWidget):
    def __init__(self, set_step: Callable, run_step: Callable):
        super().__init__()
        self.layout = QHBoxLayout(self)

        self.set_btn = QPushButton('setting')
        self.run_btn = QPushButton('run')

        self.layout.addWidget(self.set_btn)
        self.layout.addWidget(self.run_btn)

        self.set_btn.clicked.connect(set_step)
        self.run_btn.clicked.connect(run_step)
