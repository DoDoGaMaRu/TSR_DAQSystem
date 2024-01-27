from typing import Dict, List

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator, QPalette, QColor
from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QWidget, QTableWidget, QAbstractItemView, \
    QTableWidgetItem, QHeaderView, QPushButton, QGridLayout, QComboBox, QDialog, QTableView, QTextEdit, QMessageBox

from config import DAQSystemConfig, NIDeviceConfig, NIDeviceType, SensorConfig
from config.paths import BTN_ADD_NORMAL_IMG, BTN_ADD_HOVER_IMG, BTN_REMOVE_HOVER_IMG, BTN_REMOVE_NORMAL_IMG
from .setting_step import QSettingStep


class QNIDeviceSetter(QSettingStep):
    def __init__(self, conf: DAQSystemConfig):
        super().__init__()
        self._conf: DAQSystemConfig = conf
        self.selected: QTableWidgetItem = None

        """ Init main widget """
        self.device_table = QTableWidget()
        self.device_editor = QNIDeviceEditor()

        """ Init layout """
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.table_layout = QVBoxLayout()
        self.device_layout = QVBoxLayout()

        self.layout.addLayout(self.table_layout, stretch=1)
        self.layout.addLayout(self.device_layout, stretch=2)

        self._init_table_layout()
        self._init_device_layout()

        self._init_device_table()

    def _init_table_layout(self):
        self.table_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        table_title = QLabel('NI Devices')
        table_title.setFont(h1_font)
        add_button = QPushButton()
        add_button.clicked.connect(self._new_device)
        add_button.setFixedWidth(22)
        add_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_ADD_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_ADD_HOVER_IMG}");
            }}
            '''
        )
        remove_button = QPushButton()
        remove_button.clicked.connect(self._remove_device)
        remove_button.setFixedWidth(22)
        remove_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_REMOVE_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_REMOVE_HOVER_IMG}");
            }}
            '''
        )

        header_layout.addWidget(table_title, stretch=8)
        header_layout.addWidget(add_button, stretch=1)
        header_layout.addWidget(remove_button, stretch=1)

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

        self.table_layout.addLayout(header_layout)
        self.table_layout.addWidget(self.device_table)

    def _init_device_layout(self):
        self.device_layout.setContentsMargins(20, 0, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        device_layout_title = QLabel('Device Setting')
        device_layout_title.setFont(h1_font)
        self.device_editor.set_editor(None)

        button_layout = QHBoxLayout()
        reset_button = QPushButton('Reset')
        reset_button.setFixedWidth(80)
        reset_button.clicked.connect(self.device_editor.reset)
        save_button = QPushButton('Save')
        save_button.setFixedWidth(80)
        save_button.clicked.connect(self.save_device)

        button_layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignLeft, stretch=1)
        button_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight, stretch=1)
        button_layout.addStretch(2)

        self.device_layout.addWidget(device_layout_title)
        self.device_layout.addWidget(self.device_editor)
        self.device_layout.addLayout(button_layout)

    def _init_device_table(self):
        self.device_table.setRowCount(len(self._conf.NI_DEVICES))
        for idx, device in enumerate(self._conf.NI_DEVICES):
            table_item = QTableWidgetItem(device.NAME)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(idx, 0, table_item)

    def set_device_editor(self, item: QTableWidgetItem):
        self.selected = item
        self.device_editor.set_editor(self._conf.NI_DEVICES[item.row()])

    def _new_device(self):
        new_device = NIDeviceConfig(
            NAME='new_device',
            TYPE=NIDeviceType.TEMP,
            RATE=0,
            SENSORS=[]
        )
        new_device_window = QNewNIDevice(self, new_device)
        new_device_window.setModal(True)
        new_device_window.exec()

    def _remove_device(self):
        del self._conf.NI_DEVICES[self.selected.row()]
        self._init_device_table()
        self.device_editor.set_editor(None)

    def add_device(self, d_conf: NIDeviceConfig):
        self._conf.NI_DEVICES.append(d_conf)
        self._init_device_table()

    def save_device(self):
        self.device_editor.save()
        self._init_device_table()

    def valid_check(self) -> bool:
        names = []
        s_names = []
        channels = []
        for d_conf in self._conf.NI_DEVICES:
            names.append(d_conf.NAME)
            for s_conf in d_conf.SENSORS:
                s_names.append(s_conf.NAME)
                channels.append(f'{d_conf.NAME}/{s_conf.CHANNEL}')

        visited = set()
        dup_names = '\n'.join(set([x for x in names if x in visited or (visited.add(x) or False)]))
        visited = set()
        dup_s_names = '\n'.join(set([x for x in s_names if x in visited or (visited.add(x) or False)]))
        visited = set()
        dup_channels = '\n'.join(set([x for x in channels if x in visited or (visited.add(x) or False)]))

        if len(dup_names) + len(dup_s_names) + len(dup_channels) > 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.setContentsMargins(15, 15, 15, 15)
            msgBox.setModal(True)
            msgBox.setWindowTitle('Duplicate exists')
            msgBox.setText('Duplicate in the following item')
            msgBox.setInformativeText(f'NI Device name :\n{dup_names}\n\nSensor name : \n{dup_s_names}\n\nChannel : \n{dup_channels}')
            msgBox.exec()
            return False
        return True


class QNIDeviceEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.selected: QTableWidgetItem = None
        self._d_conf: NIDeviceConfig = None
        self._copy_sensors: List[SensorConfig] = None

        """ Init main widget """
        self.name_input = QLineEdit()
        self.rate_input = QLineEdit()
        self.type_input = QLineEdit()
        self.sensor_table = QTableWidget()
        self.sensor_view = QSensorView()

        """ Init layout """
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.device_layout = QVBoxLayout()
        self.sensor_layout = QVBoxLayout()

        self._init_device_layout()
        self._init_sensor_layout()

        self.layout.addLayout(self.device_layout, stretch=1)
        self.layout.addLayout(self.sensor_layout, stretch=1)

    def _init_device_layout(self):
        self.device_layout.setContentsMargins(0, 0, 0, 0)

        self.name_input.setEnabled(False)
        self.rate_input.setEnabled(False)
        self.type_input.setEnabled(False)
        self.rate_input.setValidator(QIntValidator())
        device_info_layout = QGridLayout()
        device_info_layout.setContentsMargins(0, 0, 0, 0)
        device_info_layout.addWidget(QLabel('Name : '), 0, 0)
        device_info_layout.addWidget(self.name_input, 0, 1)
        device_info_layout.addWidget(QLabel('Rate : '), 1, 0)
        device_info_layout.addWidget(self.rate_input, 1, 1)
        device_info_layout.addWidget(QLabel('Type : '), 2, 0)
        device_info_layout.addWidget(self.type_input, 2, 1)

        table_header_layout = QHBoxLayout()
        table_header_layout.setContentsMargins(0, 15, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        table_title = QLabel('Sensors')
        table_title.setFont(h1_font)
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self._new_sensor)
        self.add_button.setFixedWidth(22)
        self.add_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_ADD_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_ADD_HOVER_IMG}");
            }}
            '''
        )
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self._remove_sensor)
        self.remove_button.setFixedWidth(22)
        self.remove_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_REMOVE_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_REMOVE_HOVER_IMG}");
            }}
            '''
        )

        table_header_layout.addWidget(table_title, stretch=8)
        table_header_layout.addWidget(self.add_button, stretch=1)
        table_header_layout.addWidget(self.remove_button, stretch=1)

        self.sensor_table.setColumnCount(3)
        self.sensor_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sensor_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.sensor_table.setHorizontalHeaderLabels(['channel', 'name', 'options'])
        self.sensor_table.itemClicked.connect(self._set_selected)
        h_header = self.sensor_table.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        v_header = self.sensor_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

        self.device_layout.addLayout(device_info_layout)
        self.device_layout.addLayout(table_header_layout)
        self.device_layout.addWidget(self.sensor_table)

    def _init_sensor_layout(self):
        self.sensor_layout.setContentsMargins(20, 0, 0, 0)
        self.sensor_layout.addWidget(self.sensor_view)

    def set_editor(self, d_conf: NIDeviceConfig):
        self._d_conf = d_conf
        if self._d_conf is None:
            self.name_input.setText('')
            self.name_input.setEnabled(False)
            self.rate_input.setText('')
            self.rate_input.setEnabled(False)
            self.type_input.setText('')
            self.add_button.setEnabled(False)
            self.remove_button.setEnabled(False)
        else:
            self._copy_sensors = d_conf.SENSORS.copy()
            self.name_input.setText(self._d_conf.NAME)
            self.name_input.setEnabled(True)
            self.rate_input.setText(str(self._d_conf.RATE))
            self.rate_input.setEnabled(True)
            self.type_input.setText(self._d_conf.TYPE.name)
            self.add_button.setEnabled(True)
            self.remove_button.setEnabled(True)
        self._init_sensor_table()

    def _init_sensor_table(self):
        if self._d_conf is None:
            self.sensor_table.setRowCount(0)
        else:
            self.sensor_table.setRowCount(len(self._copy_sensors))
            for idx, s_conf in enumerate(self._copy_sensors):
                item_channel = QTableWidgetItem(s_conf.CHANNEL)
                item_channel.setFlags(item_channel.flags() & ~Qt.ItemIsEditable)
                item_name = QTableWidgetItem(s_conf.NAME)
                item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
                item_options = QTableWidgetItem(options_to_str(s_conf.OPTIONS))
                item_options.setFlags(item_options.flags() & ~Qt.ItemIsEditable)
                self.sensor_table.setItem(idx, 0, item_channel)
                self.sensor_table.setItem(idx, 1, item_name)
                self.sensor_table.setItem(idx, 2, item_options)

    def _set_selected(self, item: QTableWidgetItem):
        self.selected = item
        self.sensor_view.set_view(self._copy_sensors[item.row()])

    def reset(self):
        self.set_editor(self._d_conf)

    def save(self):
        self._d_conf.NAME = self.name_input.text()
        self._d_conf.RATE = int(self.rate_input.text())
        self._d_conf.SENSORS = self._copy_sensors

    def _new_sensor(self):
        new_sensor = SensorConfig(
            NAME='new_sensor',
            CHANNEL='',
            OPTIONS={}
        )
        if self._d_conf.TYPE is NIDeviceType.VIB:
            new_sensor_window = QNewVibSensor(self, new_sensor)
        elif self._d_conf.TYPE is NIDeviceType.TEMP:
            new_sensor_window = QNewTempSensor(self, new_sensor)
        else:
            raise RuntimeError('Invalid NIDeviceType')
        new_sensor_window.setModal(True)
        new_sensor_window.exec()

    def add_sensor(self, s_conf: SensorConfig):
        self._copy_sensors.append(s_conf)
        self._init_sensor_table()

    def _remove_sensor(self):
        self.sensor_view.set_view(None)
        del self._copy_sensors[self.selected.row()]
        self._init_sensor_table()


class QSensorView(QWidget):
    def __init__(self):
        super().__init__()
        self._s_conf = None
        self.name_input = QLineEdit()
        self.name_input.setEnabled(False)

        self.channel_input = QLineEdit()
        self.channel_input.setEnabled(False)

        self.options_input = QTextEdit()
        self.options_input.setEnabled(False)
        self.options_input.setFixedHeight(150)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(QLabel('Name : '), 0, 0)
        grid_layout.addWidget(self.name_input, 0, 1)
        grid_layout.addWidget(QLabel('Channel : '), 1, 0)
        grid_layout.addWidget(self.channel_input, 1, 1)
        grid_layout.addWidget(QLabel('Options : '), 2, 0)
        grid_layout.addWidget(self.options_input, 2, 1)

        self.layout.addLayout(grid_layout)
        self.layout.addStretch()

    def set_view(self, s_conf: SensorConfig):
        self._s_conf = s_conf
        if self._s_conf is None:
            self.name_input.setText('')
            self.channel_input.setText('')
            self.options_input.setText('')
        else:
            self.name_input.setText(self._s_conf.NAME)
            self.channel_input.setText(self._s_conf.CHANNEL)
            self.options_input.setText(options_to_str(self._s_conf.OPTIONS))


class QNewNIDevice(QDialog):
    def __init__(self, parent: QNIDeviceSetter, d_conf: NIDeviceConfig):
        super().__init__(parent)
        """ Environ """
        self.parent = parent
        self._d_conf = d_conf
        self.types = ['VIB', 'TEMP']

        """ Window """
        self.setWindowTitle('New NI Device')
        self.setFixedSize(250, 250)
        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.palette.setColor(QPalette.Window, QColor(72, 72, 72))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        """ Init main widget """
        self.name_input = QLineEdit()
        self.rate_input = QLineEdit()
        self.type_input = QComboBox()

        """ Init layout """
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.addWidget(QLabel('Name : '), 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)
        self.layout.addWidget(QLabel('Rate : '), 1, 0)
        self.layout.addWidget(self.rate_input, 1, 1)
        self.layout.addWidget(QLabel('Type : '), 2, 0)
        self.layout.addWidget(self.type_input, 2, 1)
        self.rate_input.setValidator(QIntValidator())
        for type_name in self.types:
            self.type_input.addItem(type_name)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.add_device)

        self.layout.addWidget(cancel_button, 3, 0)
        self.layout.addWidget(save_button, 3, 1)

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        self.cancel()

    def cancel(self):
        self.close()
        self.deleteLater()

    def add_device(self):
        self._d_conf.NAME = self.name_input.text()
        self._d_conf.RATE = int(self.rate_input.text())
        self._d_conf.TYPE = NIDeviceType.__members__[self.type_input.currentText()]
        self.parent.add_device(self._d_conf)
        self.cancel()


class QNewVibSensor(QDialog):
    def __init__(self, parent: QNIDeviceEditor, s_conf: SensorConfig):
        super().__init__(parent)
        """ Environ """
        self.parent = parent
        self._s_conf: SensorConfig = s_conf

        """ Window """
        self.setWindowTitle('New Sensor')
        self.setFixedSize(250, 250)
        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.palette.setColor(QPalette.Window, QColor(72, 72, 72))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        """ Init main widget """
        self.name_input = QLineEdit()
        self.channel_input = QLineEdit()
        self.sensitivity_input = QLineEdit()

        """ Init layout """
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.addWidget(QLabel('Name : '), 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)
        self.layout.addWidget(QLabel('Channel(ai) : '), 1, 0)
        self.layout.addWidget(self.channel_input, 1, 1)
        self.layout.addWidget(QLabel('Sensitivity : '), 2, 0)
        self.layout.addWidget(self.sensitivity_input, 2, 1)
        self.channel_input.setValidator(QIntValidator())
        self.sensitivity_input.setValidator(QIntValidator())

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.add_sensor)

        self.layout.addWidget(cancel_button, 3, 0)
        self.layout.addWidget(save_button, 3, 1)

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        self.deleteLater()

    def cancel(self):
        self.close()

    def add_sensor(self):
        self._s_conf.NAME = self.name_input.text()
        self._s_conf.CHANNEL = f'ai{int(self.channel_input.text())}'
        self._s_conf.OPTIONS = {
            'sensitivity': int(self.sensitivity_input.text())
        }
        self.parent.add_sensor(self._s_conf)
        self.cancel()


class QNewTempSensor(QDialog):
    def __init__(self, parent: QNIDeviceEditor, s_conf: SensorConfig):
        super().__init__(parent)
        """ Environ """
        self.parent = parent
        self._s_conf: SensorConfig = s_conf

        """ Window """
        self.setWindowTitle('New Sensor')
        self.setFixedSize(250, 250)
        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.palette.setColor(QPalette.Window, QColor(72, 72, 72))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        """ Init main widget """
        self.name_input = QLineEdit()
        self.channel_input = QLineEdit()
        self.sensitivity_input = QLineEdit()

        """ Init layout """
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.addWidget(QLabel('Name : '), 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)
        self.layout.addWidget(QLabel('Channel(ai) : '), 1, 0)
        self.layout.addWidget(self.channel_input, 1, 1)
        self.channel_input.setValidator(QIntValidator())
        self.sensitivity_input.setValidator(QIntValidator())

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.add_sensor)

        self.layout.addWidget(cancel_button, 3, 0)
        self.layout.addWidget(save_button, 3, 1)

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        self.deleteLater()

    def cancel(self):
        self.close()

    def add_sensor(self):
        self._s_conf.NAME = self.name_input.text()
        self._s_conf.CHANNEL = f'ai{int(self.channel_input.text())}'
        self.parent.add_sensor(self._s_conf)
        self.cancel()


def options_to_str(options: Dict) -> str:
    res = ''
    for key, value in options.items():
        res += f'{key}: {str(value)}\n'
    return res

