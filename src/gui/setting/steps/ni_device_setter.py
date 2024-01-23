from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QWidget, QTableWidget, QAbstractItemView, \
    QTableWidgetItem, QHeaderView

from config import DAQSystemConfig, NIDeviceConfig
from .setting_step import QSettingStep


class QNIDeviceSetter(QSettingStep):
    def __init__(self, conf: DAQSystemConfig):
        super().__init__()
        self._conf: DAQSystemConfig = conf
        self._d_confs: Dict[str, NIDeviceConfig] = {}

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.device_table = QTableWidget()
        self.device_editor = QNIDeviceEditor()

        self.layout.addWidget(self.device_table, stretch=1)
        self.layout.addWidget(self.device_editor, stretch=4)

        self._init_device_table()
        self._init_device_editor()

        self.set_device_table()

    def _init_device_table(self):
        self.device_table.setColumnCount(1)
        self.device_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.device_table.itemClicked.connect(self.set_device_editor)
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.device_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.device_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

    def _init_device_editor(self):
        pass

    def valid_check(self) -> bool:
        return True

    def set_device_table(self):
        self._d_confs = {d_conf.NAME: d_conf for d_conf in self._conf.NI_DEVICES}
        self.device_table.setRowCount(len(self._conf.NI_DEVICES))
        for idx, sensor in enumerate(self._d_confs.keys()):
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(idx, 0, table_item)

    def set_device_editor(self, item: QTableWidgetItem):
        self.device_editor.set_editor(self._d_confs[item.text()], item)


class QNIDeviceEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._d_conf = None
        self.layout = QVBoxLayout(self)
        self.set_name = QHBoxLayout()
        self.set_rate = QHBoxLayout()

        self.name_label = QLabel('name : ')
        self.rate_label = QLabel('rate : ')
        self.name_input = QLineEdit(self)
        self.rate_input = QLineEdit(self)

        self.set_name.addWidget(self.name_label, stretch=2)
        self.set_name.addWidget(self.name_input, stretch=5)

        self.set_rate.addWidget(self.rate_label, stretch=2)
        self.set_rate.addWidget(self.rate_input, stretch=5)

        self.layout.addLayout(self.set_name)
        self.layout.addLayout(self.set_rate)

    def set_editor(self, d_conf: NIDeviceConfig, target: QTableWidgetItem):
        self._d_conf = d_conf

    def reset_editor(self):
        pass

    def valid_check(self) -> bool:
        return True


class QSensorSetting(QSettingStep):
    def valid_check(self) -> bool:
        return True
