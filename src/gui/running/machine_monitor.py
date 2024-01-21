from typing import List, Dict

from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel

from background.machine import Machine
from .machine import QMachine


class QMachineMonitor(QWidget):
    def __init__(self, machines: List[Machine]):
        super().__init__()
        self._machines: Dict[str, Machine] = {m.get_name(): m for m in machines}

        self.layout = QVBoxLayout(self)

        self.header_layout = QHBoxLayout()
        self.content_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self.layout.addLayout(self.header_layout, 2)
        self.layout.addLayout(self.content_layout, 20)
        self.layout.addLayout(self.bottom_layout, 1)

        self._init_content()
        self._init_header()
        self._init_bottom()

    def _init_header(self):
        self.header_layout.setContentsMargins(27, 20, 27, 0)

        self.drop_down = QComboBox()
        self.drop_down.setFixedWidth(180)

        self.drop_down.currentTextChanged.connect(self.set_machine)
        for name in self._machines.keys():
            self.drop_down.addItem(name)

        self.header_layout.addWidget(QLabel('Select '))
        self.header_layout.addWidget(self.drop_down)
        self.header_layout.addStretch()

    def _init_content(self):
        # TODO 헤더에 네비게이션 추가하고, 콘솔창도 볼 수 있게
        self.content_layout.setContentsMargins(0, 0, 27, 0)

        self.machine_widget = QMachine(self)
        self.content_layout.addWidget(self.machine_widget)

    def _init_bottom(self):
        self.bottom_layout.setContentsMargins(27, 0, 27, 0)

    @QtCore.Slot()
    def set_machine(self, machine_name):
        self.machine_widget.set_machine(self._machines[machine_name])
