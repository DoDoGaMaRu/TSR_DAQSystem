import shutil
import tarfile
from typing import List

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator, QCloseEvent, QPalette, QColor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QWidget, QLabel, QPushButton, QAbstractItemView, \
    QHeaderView, QTableWidgetItem, QLineEdit, QCheckBox, QGridLayout, QFileDialog, QDialog, QMessageBox

from config import DAQSystemConfig, MachineConfig, DataSendModeConfig, DataSaveModeConfig
from config.paths import BTN_ADD_NORMAL_IMG, BTN_ADD_HOVER_IMG, BTN_REMOVE_NORMAL_IMG, BTN_REMOVE_HOVER_IMG, \
    BTN_LEFT_NORMAL_IMG, BTN_LEFT_HOVER_IMG, BTN_RIGHT_HOVER_IMG, BTN_RIGHT_NORMAL_IMG, BTN_FOLDER_FIND_IMG, MODEL_DIR
from lib.lstm_ae import ModelConfig
from .setting_step import QSettingStep


class QMachineSetter(QSettingStep):
    def __init__(self, conf: DAQSystemConfig):
        super().__init__()
        self.selected_m: QTableWidgetItem = None
        self.selected_s: QTableWidgetItem = None
        self._conf: DAQSystemConfig = conf

        """ Init main widget """
        self.machine_table = QTableWidget()
        self.machine_editor = QMachineEditor()
        self.sensor_table = QTableWidget()

        """ Init layout """
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.m_table_layout = QVBoxLayout()
        self.machine_layout = QVBoxLayout()
        self.s_table_layout = QHBoxLayout()

        self._init_m_tabel_layout()
        self._init_machine_layout()
        self._init_s_table_layout()

        self.layout.addLayout(self.m_table_layout, stretch=1)
        self.layout.addLayout(self.machine_layout, stretch=1)
        self.layout.addLayout(self.s_table_layout, stretch=1)

        """ Init main widget """
        self._init_machine_table()
        self._init_sensor_table()

    def _init_m_tabel_layout(self):
        self.m_table_layout.setContentsMargins(0, 0, 0, 0)

        table_header_layout = QHBoxLayout()
        table_header_layout.setContentsMargins(0, 0, 0, 0)
        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        table_title = QLabel('Machines')
        table_title.setFont(h1_font)
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self._new_machine)
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
        self.remove_button.clicked.connect(self._remove_machine)
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

        self.machine_table.setColumnCount(1)
        self.machine_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.machine_table.itemClicked.connect(self.select_machine)
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.machine_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.machine_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

        self.m_table_layout.addLayout(table_header_layout)
        self.m_table_layout.addWidget(self.machine_table)

    def _init_machine_layout(self):
        self.machine_layout.setContentsMargins(20, 0, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        layout_title = QLabel('Machine Setting')
        layout_title.setFont(h1_font)
        self.machine_editor.set_editor(None)

        button_layout = QHBoxLayout()
        reset_button = QPushButton('Reset')
        reset_button.setFixedWidth(80)
        reset_button.clicked.connect(self.reset_editor)
        save_button = QPushButton('Save')
        save_button.setFixedWidth(80)
        save_button.clicked.connect(self.save_machine)

        button_layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignLeft, stretch=1)
        button_layout.addStretch(2)
        button_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight, stretch=1)

        self.machine_layout.addWidget(layout_title)
        self.machine_layout.addWidget(self.machine_editor)
        self.machine_layout.addLayout(button_layout)

    def _init_s_table_layout(self):
        self.s_table_layout.setContentsMargins(0, 150, 0, 0)

        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        left_button = QPushButton()
        left_button.clicked.connect(self.include_sensor)
        left_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_LEFT_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_LEFT_HOVER_IMG}");
            }}
            '''
        )
        right_button = QPushButton()
        right_button.clicked.connect(self.exclude_sensor)
        right_button.setStyleSheet(
            f'''
            QPushButton {{
                background-color: transparent; 
                border: none;
                image: url("{BTN_RIGHT_NORMAL_IMG}");
            }}
            QPushButton:hover {{
                image: url("{BTN_RIGHT_HOVER_IMG}");
            }}
            '''
        )
        button_layout.addStretch()
        button_layout.addWidget(left_button)
        button_layout.addWidget(right_button)
        button_layout.addStretch()

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        table_title = QLabel('Excluded Sensors')
        table_title.setFont(h1_font)
        self.sensor_table.setColumnCount(1)
        self.sensor_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sensor_table.itemClicked.connect(self.select_sensor)
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.sensor_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.sensor_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.sensor_table)

        self.s_table_layout.addLayout(button_layout)
        self.s_table_layout.addLayout(table_layout)

    def _init_machine_table(self):
        self.machine_table.setRowCount(len(self._conf.MACHINES))
        for idx, machine in enumerate(self._conf.MACHINES):
            table_item = QTableWidgetItem(machine.NAME)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.machine_table.setItem(idx, 0, table_item)

    def _init_sensor_table(self):
        non_selected_sensors = []
        selected_sensors = []
        for d_conf in self._conf.NI_DEVICES:
            non_selected_sensors += [s_conf.NAME for s_conf in d_conf.SENSORS]
        for m_conf in self._conf.MACHINES:
            selected_sensors += m_conf.SENSORS
        for sensor in selected_sensors:
            non_selected_sensors.remove(sensor)

        self.sensor_table.setRowCount(len(non_selected_sensors))
        for idx, sensor in enumerate(non_selected_sensors):
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.sensor_table.setItem(idx, 0, table_item)

    def select_machine(self, item: QTableWidgetItem):
        self.selected_m = item
        self.machine_editor.set_editor(self._conf.MACHINES[item.row()])
        self._init_sensor_table()

    def select_sensor(self, item: QTableWidgetItem):
        self.selected_s = item

    def _new_machine(self):
        new_m_conf = MachineConfig(
            NAME='new_machine',
            SENSORS=[],
            FAULT_DETECTABLE=False,
            FAULT_THRESHOLD=0,
            DATA_SAVE_MODE=DataSaveModeConfig(ACTIVATION=False),
            DATA_SEND_MODE=DataSendModeConfig(ACTIVATION=False)
        )
        self._conf.MACHINES.append(new_m_conf)
        self._init_machine_table()
        self._init_sensor_table()

    def _remove_machine(self):
        del self._conf.MACHINES[self.selected_m.row()]
        self._init_machine_table()
        self._init_sensor_table()
        self.machine_editor.set_editor(None)

    def reset_editor(self):
        self._init_sensor_table()
        self.machine_editor.reset()

    def save_machine(self):
        self.machine_editor.save()
        self._init_machine_table()
        self._init_sensor_table()

    def include_sensor(self):
        try:
            self.machine_editor.include_sensor(self.selected_s.text())
            self.sensor_table.removeRow(self.selected_s.row())
        except:
            pass

    def exclude_sensor(self):
        sensor = self.machine_editor.get_selected_sensor()

        if sensor is not None:
            self.machine_editor.exclude_sensor(sensor)

            insert_idx = self.sensor_table.rowCount()
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.sensor_table.setRowCount(insert_idx+1)
            self.sensor_table.setItem(insert_idx, 0, table_item)

    def valid_check(self) -> bool:
        names = [m_conf.NAME for m_conf in self._conf.MACHINES]
        visited = set()
        dup_names = '\n'.join(set([x for x in names if x in visited or (visited.add(x) or False)]))

        if len(dup_names) > 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.setContentsMargins(15, 15, 15, 15)
            msgBox.setModal(True)
            msgBox.setWindowTitle('Duplicate exists')
            msgBox.setText('Duplicate in the following item')
            msgBox.setInformativeText(f'Machine name :\n{dup_names}')
            msgBox.exec()
            return False
        return True


class QMachineEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._m_conf: MachineConfig = None
        self.selected_s: QTableWidgetItem = None
        self.copy_sensors = []

        """ Init main widget """
        self.name_input = QLineEdit()
        self.fault_detect_checkbox = QCheckBox()
        self.fault_detect_threshold = QLineEdit()
        self.save_checkbox = QCheckBox()
        self.save_path_input = QLineEdit()
        self.send_checkbox = QCheckBox()
        self.send_host_input = QLineEdit()
        self.send_port_input = QLineEdit()
        self.sensor_table = QTableWidget()
        self.set_model_button = QPushButton('Select Model')
        self.set_save_path_btn = QPushButton()
        self._init_main_widget()

        """ Init layout """
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.machine_layout = QVBoxLayout()
        self.sensor_layout = QVBoxLayout()

        self._init_machine_layout()
        self._init_sensor_layout()

        self.layout.addLayout(self.machine_layout)
        self.layout.addLayout(self.sensor_layout)

    def _init_main_widget(self):
        self.set_save_path_btn.clicked.connect(self.set_save_path)
        self.set_save_path_btn.setFixedWidth(22)
        self.set_save_path_btn.setStyleSheet(
                f'''
                QPushButton {{
                    background-color: transparent; 
                    border: 1px solid transparent;
                    image: url("{BTN_FOLDER_FIND_IMG}");
                }}
                QPushButton:hover {{
                    border-color: green;
                }}
                '''
            )

        self.fault_detect_checkbox.stateChanged.connect(self.fd_state_change)
        self.save_checkbox.stateChanged.connect(self.save_state_change)
        self.send_checkbox.stateChanged.connect(self.send_state_change)

        self.set_model_button.clicked.connect(self.register_model)
        self.fault_detect_threshold.setPlaceholderText('Threshold')
        self.fault_detect_threshold.setMaximumWidth(80)
        self.fault_detect_threshold.setValidator(QIntValidator())

        self.send_host_input.setPlaceholderText('Host')
        self.send_port_input.setPlaceholderText('Port')
        self.send_port_input.setMaximumWidth(80)
        self.send_port_input.setValidator(QIntValidator())

        self.sensor_table.setColumnCount(1)
        self.sensor_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sensor_table.itemClicked.connect(self.select_sensor)
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.sensor_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.sensor_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

    def _init_machine_layout(self):
        self.machine_layout.setContentsMargins(0, 0, 0, 0)

        info_layout = QGridLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)

        info_layout.addWidget(QLabel('Name : '), 0, 0)
        info_layout.addWidget(self.name_input, 0, 2, 1, 2)

        info_layout.addWidget(QLabel('Fault Detect : '), 1, 0)
        info_layout.addWidget(self.fault_detect_checkbox, 1, 1)
        info_layout.addWidget(self.set_model_button, 1, 2)
        info_layout.addWidget(self.fault_detect_threshold, 1, 3)

        info_layout.addWidget(QLabel('Data Save : '), 2, 0)
        info_layout.addWidget(self.save_checkbox, 2, 1)
        info_layout.addWidget(self.save_path_input, 2, 2, 1, 2)
        info_layout.addWidget(self.set_save_path_btn, 2, 4)

        info_layout.addWidget(QLabel('Data Send : '), 3, 0)
        info_layout.addWidget(self.send_checkbox, 3, 1)
        info_layout.addWidget(self.send_host_input, 3, 2)
        info_layout.addWidget(self.send_port_input, 3, 3)

        self.machine_layout.addLayout(info_layout)

    def _init_sensor_layout(self):
        self.sensor_layout.setContentsMargins(0, 12, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        table_title = QLabel('Included Sensors')
        table_title.setFont(h1_font)

        self.sensor_layout.addWidget(table_title)
        self.sensor_layout.addWidget(self.sensor_table)

    def fd_state_change(self):
        if self.fault_detect_checkbox.isChecked():
            self.set_model_button.setEnabled(True)
            self.fault_detect_threshold.setEnabled(True)
        else:
            self.set_model_button.setEnabled(False)
            self.fault_detect_threshold.setEnabled(False)

    def save_state_change(self):
        if self.save_checkbox.isChecked():
            self.save_path_input.setEnabled(True)
            self.set_save_path_btn.setEnabled(True)
        else:
            self.save_path_input.setEnabled(False)
            self.set_save_path_btn.setEnabled(False)

    def send_state_change(self):
        if self.send_checkbox.isChecked():
            self.send_host_input.setEnabled(True)
            self.send_port_input.setEnabled(True)
        else:
            self.send_host_input.setEnabled(False)
            self.send_port_input.setEnabled(False)

    def set_save_path(self):
        dir_path = QFileDialog.getExistingDirectory(None, "Select Directory", "", QFileDialog.Option.ShowDirsOnly)
        if dir_path:
            self.save_path_input.setText(dir_path)

    def set_editor(self, m_conf: MachineConfig):
        self._m_conf = m_conf
        if self._m_conf is None:
            self.setEnabled(False)
            self.copy_sensors = []
            self._init_sensor_table()
        else:
            self.setEnabled(True)
            self.copy_sensors = m_conf.SENSORS.copy()
            self.name_input.setText(self._m_conf.NAME)

            self.fault_detect_checkbox.setChecked(self._m_conf.FAULT_DETECTABLE)
            self.fault_detect_threshold.setText(str(self._m_conf.FAULT_THRESHOLD))

            self.save_checkbox.setChecked(self._m_conf.DATA_SAVE_MODE.ACTIVATION)
            self.save_path_input.setText(self._m_conf.DATA_SAVE_MODE.PATH)

            self.send_checkbox.setChecked(self._m_conf.DATA_SEND_MODE.ACTIVATION)
            self.send_host_input.setText(self._m_conf.DATA_SEND_MODE.HOST)
            self.send_port_input.setText(str(self._m_conf.DATA_SEND_MODE.PORT))
            self._init_sensor_table()
        self.fd_state_change()
        self.save_state_change()
        self.send_state_change()

    def _init_sensor_table(self):
        self.sensor_table.setRowCount(len(self.copy_sensors))
        for idx, sensor in enumerate(self.copy_sensors):
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.sensor_table.setItem(idx, 0, table_item)

    def reset(self):
        self.set_editor(self._m_conf)

    def save(self):
        self._m_conf.NAME = self.name_input.text()

        self._m_conf.FAULT_DETECTABLE = self.fault_detect_checkbox.isChecked()
        self._m_conf.FAULT_THRESHOLD = int(self.fault_detect_threshold.text())

        self._m_conf.DATA_SAVE_MODE.ACTIVATION = self.save_checkbox.isChecked()
        self._m_conf.DATA_SAVE_MODE.PATH = self.save_path_input.text()

        self._m_conf.DATA_SEND_MODE.ACTIVATION = self.send_checkbox.isChecked()
        self._m_conf.DATA_SEND_MODE.HOST = self.send_host_input.text()
        self._m_conf.DATA_SEND_MODE.PORT = int(self.send_port_input.text())
        self._m_conf.DATA_SEND_MODE.TIMEOUT = 60

        self._m_conf.SENSORS = self.copy_sensors

    def select_sensor(self, item: QTableWidgetItem):
        self.selected_s = item

    def get_selected_sensor(self) -> str:
        try:
            return self.selected_s.text()
        except:
            return None

    def include_sensor(self, sensor):
        self.copy_sensors.append(sensor)
        self._init_sensor_table()

    def exclude_sensor(self, sensor):
        try:
            self.copy_sensors.remove(sensor)
            self._init_sensor_table()
        except:
            pass

    def register_model(self):
        register_model_window = QSelectModel(self._m_conf.NAME, self.copy_sensors)
        register_model_window.setModal(True)
        register_model_window.exec()


class QSelectModel(QDialog):
    def __init__(self, machine_name: str, sensors: List[str]):
        super().__init__()
        self.model_confs: List[ModelConfig] = []
        self.machine_name = machine_name
        self.sensors = sensors

        """ Window """
        self.setWindowTitle('Model Load')
        self.setFixedSize(350, 350)
        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.palette.setColor(QPalette.Window, QColor(72, 72, 72))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        """ Init main widget """
        self.model_path_input = QLineEdit()
        self.find_model_btn = QPushButton()
        self.check_model_btn = QPushButton('Check')
        self.sensor_table = QTableWidget()
        self.model_table = QTableWidget()
        self._init_main_widget()

        """ Init layout """
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.select_layout = QHBoxLayout()
        self.compare_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self._init_select_layout()
        self._init_compare_layout()
        self._init_bottom_layout()

        self.layout.addLayout(self.select_layout)
        self.layout.addLayout(self.compare_layout)
        self.layout.addLayout(self.bottom_layout)

    def _init_main_widget(self):
        self.find_model_btn.clicked.connect(self.set_model_path)
        self.find_model_btn.setFixedWidth(22)
        self.find_model_btn.setStyleSheet(
            f'''
                QPushButton {{
                    background-color: transparent; 
                    border: 1px solid transparent;
                    image: url("{BTN_FOLDER_FIND_IMG}");
                }}
                QPushButton:hover {{
                    border-color: green;
                }}
                '''
        )
        self.check_model_btn.clicked.connect(self.check_model)

        self.sensor_table.setColumnCount(1)
        self.sensor_table.setRowCount(len(self.sensors))
        for idx, sensor in enumerate(self.sensors):
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.sensor_table.setItem(idx, 0, table_item)
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.sensor_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.sensor_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

        self.model_table.setColumnCount(1)
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.model_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.model_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

    def _init_select_layout(self):
        self.select_layout.setContentsMargins(0, 0, 0, 0)

        self.select_layout.addWidget(self.model_path_input)
        self.select_layout.addWidget(self.find_model_btn)
        self.select_layout.addWidget(self.check_model_btn)

    def _init_compare_layout(self):
        self.compare_layout.setContentsMargins(0, 0, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)

        sensor_title = QLabel('Sensors')
        sensor_title.setFont(h1_font)
        sensor_layout = QVBoxLayout()
        sensor_layout.setContentsMargins(0, 10, 0, 0)
        sensor_layout.addWidget(sensor_title)
        sensor_layout.addWidget(self.sensor_table)

        model_title = QLabel('Models')
        model_title.setFont(h1_font)
        model_layout = QVBoxLayout()
        model_layout.setContentsMargins(0, 10, 0, 0)
        model_layout.addWidget(model_title)
        model_layout.addWidget(self.model_table)

        self.compare_layout.addLayout(sensor_layout)
        self.compare_layout.addLayout(model_layout)

    def _init_bottom_layout(self):
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)
        finish_button = QPushButton('Finish')
        finish_button.clicked.connect(self.finish)

        self.bottom_layout.addWidget(cancel_button)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(finish_button)

    def _init_model_table(self):
        self.model_table.setRowCount(len(self.model_confs))
        for idx, model_conf in enumerate(self.model_confs):
            table_item = QTableWidgetItem(model_conf.NAME)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.model_table.setItem(idx, 0, table_item)

    def set_model_path(self):
        model_path, _ = QFileDialog.getOpenFileName(None, "Select Model", "", filter='*.tar')
        if model_path:
            self.model_path_input.setText(model_path)

    def check_model(self):
        model_path = self.model_path_input.text()
        with tarfile.open(model_path, 'r') as tar_file:
            tar_file.extractall(path=f'{MODEL_DIR}\\{self.machine_name}')

        try:
            with open(f'{MODEL_DIR}\\{self.machine_name}\\METADATA.yml', 'r', encoding='UTF-8') as yml:
                cfg = yaml.safe_load(yml)
                self.model_confs = [ModelConfig(**parm) for parm in cfg['MODELS']]
        except:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.setContentsMargins(15, 15, 15, 15)
            msgBox.setModal(True)
            msgBox.setWindowTitle('Select Model')
            msgBox.setText('Invalid Model File')
            msgBox.exec()
        self._init_model_table()

    def finish(self):
        self.close()
        self.deleteLater()

    def cancel(self):
        try:
            shutil.rmtree(f'{MODEL_DIR}\\{self.machine_name}')
        except:
            pass
        self.close()
        self.deleteLater()
