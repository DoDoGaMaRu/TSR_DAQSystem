from typing import Dict

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel

from background import DAQSystem
from background.machine import Machine
from config import MachineConfig
from .machine import QMachine


class QDAQSystemMonitor(QWidget):
    set_monitoring_target = Signal(Machine)

    def __init__(self, bg_system: DAQSystem):
        super().__init__()
        """ Set environ """
        self._bg_system = bg_system
        self._conf = self._bg_system.get_conf()

        self._machines: Dict[str, Machine] = {m.get_name(): m for m in bg_system.get_machines()}
        self._m_confs: Dict[str, MachineConfig] = {m_conf.NAME: m_conf for m_conf in self._conf.MACHINES}

        """ Set main components """
        self.machine_widget = QMachine(self)
        self._bg_system.event_signal.connect(self.machine_widget.event_handle)
        self.set_monitoring_target.connect(self._bg_system.set_monitoring_target)

        """ Set layout """
        self.layout = QVBoxLayout(self)

        self.header_layout = QHBoxLayout()
        self.content_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self.layout.addLayout(self.header_layout, 2)
        self.layout.addLayout(self.content_layout, 20)
        self.layout.addLayout(self.bottom_layout, 1)

        self._init_header()
        self._init_content()
        self._init_bottom()

    def _init_header(self):
        self.header_layout.setContentsMargins(18, 0, 18, 0)

        self.drop_down = QComboBox()
        self.drop_down.setFixedWidth(180)

        self.drop_down.currentTextChanged.connect(self.set_machine)
        for name in self._machines.keys():
            self.drop_down.addItem(name)

        self.header_layout.addWidget(QLabel('Select Machine : '))
        self.header_layout.addWidget(self.drop_down)
        self.header_layout.addStretch()

    def _init_content(self):
        self.content_layout.setContentsMargins(0, 0, 18, 0)
        self.content_layout.addWidget(self.machine_widget)

    def _init_bottom(self):
        self.bottom_layout.setContentsMargins(18, 0, 18, 0)

    def set_machine(self, machine_name):
        self.machine_widget.set_machine(self._m_confs[machine_name])
        self.set_monitoring_target.emit(self._machines[machine_name])
