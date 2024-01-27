from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QPushButton

from config import ConfigLoader
from .steps import QMachineSetter, QNIDeviceSetter, QSettingStep


class QSettingWidget(QWidget):
    setting_end = Signal()

    def __init__(self):
        super().__init__()
        self.cur_step: int = 1
        self._conf = ConfigLoader.load_conf()

        # Set Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 17, 30, 17)

        self.header_layout = QHBoxLayout()
        self.content_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self.layout.addLayout(self.header_layout, 1)
        self.layout.addLayout(self.content_layout, 10)
        self.layout.addLayout(self.bottom_layout, 2)

        self._init_header()
        self._init_content()
        self._init_bottom()

        self._init_setting_steps()

        self.go_step(self.cur_step)

    def _init_header(self):
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.step_label = QLabel()
        self.header_layout.addWidget(self.step_label)

    def _init_content(self):
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.central_frame = QStackedWidget()
        self.central_frame.addWidget(QSettingStep())
        self.content_layout.addWidget(self.central_frame)

    def _init_bottom(self):
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton(text='Cancel')
        self.cancel_button.clicked.connect(self.setting_end.emit)

        self.next_button = QPushButton(text='Next')
        self.next_button.clicked.connect(self.next)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.next_button)

        self.bottom_layout.addLayout(button_layout)

    def go_step(self, step: int):
        if 0 < step < self.central_frame.count():
            self.cur_step = step
            self.central_frame.setCurrentIndex(step)
            self.step_label.setText(f'step {self.cur_step} of {self.central_frame.count()-1}')

    def next(self):
        if self.central_frame.widget(self.cur_step).valid_check():
            next_step = self.cur_step + 1
            if next_step == self.central_frame.count()-1:
                self.next_button.setText('Finish')

            if next_step < self.central_frame.count():
                self.go_step(next_step)
            else:
                ConfigLoader.save_conf(self._conf)
                self.setting_end.emit()

    def _init_setting_steps(self):
        self.central_frame.addWidget(QNIDeviceSetter(self._conf))
        self.central_frame.addWidget(QMachineSetter(self._conf))
