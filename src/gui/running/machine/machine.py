import os
from typing import List, Dict, Tuple
from scipy import signal

from PySide6 import QtCore
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPalette, QColor, QDesktopServices
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QStackedWidget, QTableWidget, QTableWidgetItem, \
    QHeaderView, QAbstractItemView, QPushButton, QGridLayout

from background.machine.machine_event import MachineEvent
from config import MachineConfig, DataSaveModeConfig, DataSendModeConfig
from config.paths import BTN_FOLDER_ENABLE_IMG, BTN_FOLDER_DISABLE_IMG
from .realtime_chart import QRealtimeChart


MAXIMUM_VIEW = 400
MAXIMUM_BATCH = int(MAXIMUM_VIEW * 0.05)


class QMachine(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        """ Set environ """
        self._m_conf: MachineConfig = None
        self.charts: Dict[str, QRealtimeChart] = {}

        """ Set layout """
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.chart_layout = QVBoxLayout()
        self.control_layout = QVBoxLayout()
        self._init_chart_layout()
        self._init_control_layout()

        self.layout.addLayout(self.chart_layout, stretch=7)
        self.layout.addLayout(self.control_layout, stretch=2)

    def _init_chart_layout(self) -> None:
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_stack = QStackedWidget()
        self.chart_stack.setContentsMargins(0, 0, 0, 0)
        self.chart_layout.addWidget(self.chart_stack)

    def _init_control_layout(self) -> None:
        """ Set machine information """
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 15, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        info_title = QLabel('Machine Info')
        info_title.setFont(h1_font)

        info_grid_layout = QGridLayout()
        info_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel()
        info_grid_layout.addWidget(QLabel('Name : '), 0, 0)
        info_grid_layout.addWidget(self.name_label, 0, 1)

        self.fd_info_label = QLabel()
        info_grid_layout.addWidget(QLabel('Fault Detector : '), 1, 0)
        info_grid_layout.addWidget(self.fd_info_label, 1, 1)

        dsave_layout = QHBoxLayout()
        dsave_layout.setContentsMargins(0, 0, 0, 0)
        self.dsave_activated_label = QLabel()
        self.open_dir_btn = QPushButton()
        self.open_dir_btn.clicked.connect(self._open_folder)
        self.open_dir_btn.setFixedWidth(22)
        dsave_layout.addWidget(self.dsave_activated_label)
        dsave_layout.addWidget(self.open_dir_btn, alignment=Qt.AlignmentFlag.AlignRight)
        info_grid_layout.addWidget(QLabel('Data Save Mode : '), 2, 0)
        info_grid_layout.addLayout(dsave_layout, 2, 1)

        self.dsend_activated_label = QLabel()
        self.dsend_address_label = QLabel()
        info_grid_layout.addWidget(QLabel('Data Send Mode : '), 3, 0)
        info_grid_layout.addWidget(self.dsend_activated_label, 3, 1)
        info_grid_layout.addWidget(self.dsend_address_label, 4, 1)

        info_layout.addWidget(info_title)
        info_layout.addLayout(info_grid_layout)

        """ Set sensor selection layout """
        ss_layout = QVBoxLayout()
        ss_layout.setContentsMargins(0, 20, 0, 0)

        ss_title = QLabel('Sensors')
        ss_title.setFont(h1_font)

        self.sensor_table = QTableWidget()
        self.sensor_table.setColumnCount(1)
        self.sensor_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sensor_table.itemClicked.connect(lambda item: self.chart_stack.setCurrentIndex(item.row()))
        resize = QHeaderView.ResizeMode.Stretch
        h_header = self.sensor_table.horizontalHeader()
        h_header.setSectionResizeMode(resize)
        h_header.hide()
        v_header = self.sensor_table.verticalHeader()
        v_header.setAutoScroll(True)
        v_header.hide()

        ss_layout.addWidget(ss_title)
        ss_layout.addWidget(self.sensor_table)

        """ Set fault detection result layout """
        fd_layout = QVBoxLayout()
        fd_layout.setContentsMargins(0, 20, 0, 17)

        fd_title = QLabel('Fault Detect')
        fd_title.setFont(h1_font)

        fd_res_font = QFont()
        fd_res_font.setBold(True)
        fd_res_font.setPointSize(14)
        self.fd_res_palette = QPalette()
        self.fd_res_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.fd_res_label = QLabel()
        self.fd_res_label.setFont(fd_res_font)
        self.fd_res_label.setFixedHeight(50)
        self.fd_res_label.setAutoFillBackground(True)
        self.fd_res_label.setPalette(self.fd_res_palette)
        self.fd_res_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        fd_value_layout = QHBoxLayout()
        self.fd_score_label = QLabel('0')
        self.fd_threshold_label = QLabel('0')
        fd_value_layout.addWidget(QLabel('fault score : '))
        fd_value_layout.addWidget(self.fd_score_label)
        fd_value_layout.addWidget(QLabel('threshold : '))
        fd_value_layout.addWidget(self.fd_threshold_label)

        fd_layout.addWidget(fd_title)
        fd_layout.addWidget(self.fd_res_label)
        fd_layout.addLayout(fd_value_layout)

        """ Set control layout """
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.addLayout(info_layout)
        self.control_layout.addLayout(ss_layout)
        self.control_layout.addLayout(fd_layout)

    def _set_control_layout(self) -> None:
        while self.chart_stack.count():
            widget = self.chart_stack.widget(0)
            if widget:
                widget.deleteLater()
                self.chart_stack.removeWidget(widget)
        self.charts = {}

        self.name_label.setText(self._m_conf.NAME)

        if self._m_conf.FAULT_DETECTABLE:
            self.fd_info_label.setText('Running')
            self.fault_detect_normal()
        else:
            self.fd_info_label.setText('Disable')
            self.fault_detect_disable()

        dsave_conf: DataSaveModeConfig = self._m_conf.DATA_SAVE_MODE
        if dsave_conf.ACTIVATION:
            self.dsave_activated_label.setText('Enable')
            self.open_dir_btn.setEnabled(True)
            self.open_dir_btn.setStyleSheet(
                f'''
                QPushButton {{
                    background-color: transparent; 
                    border: 1px solid transparent;
                    image: url("{BTN_FOLDER_ENABLE_IMG}");
                }}
                QPushButton:hover {{
                    border-color: green;
                }}
                '''
            )
        else:
            self.dsave_activated_label.setText('Disable')
            self.open_dir_btn.setEnabled(False)
            self.open_dir_btn.setStyleSheet(
                f'''
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    image: url("{BTN_FOLDER_DISABLE_IMG}");
                }}
                '''
            )

        dsend_conf: DataSendModeConfig = self._m_conf.DATA_SEND_MODE
        if dsend_conf.ACTIVATION:
            self.dsend_activated_label.setText('Enable')
            self.dsend_address_label.setText(f'{dsend_conf.HOST}:{dsend_conf.PORT}')
        else:
            self.dsend_activated_label.setText('Disable')
            self.dsend_address_label.setText(' ')

        sensors: List[str] = self._m_conf.SENSORS
        self.sensor_table.setRowCount(len(sensors))
        for idx, sensor in enumerate(sensors):
            new_chart = QRealtimeChart(self, sensor, MAXIMUM_VIEW)
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.sensor_table.setItem(idx, 0, table_item)
            self.chart_stack.addWidget(new_chart)
            self.charts[sensor] = new_chart

    def fault_detect_disable(self) -> None:
        self.fd_res_label.setText('DISABLE')
        self.fd_res_palette.setColor(QPalette.Window, QColor(120, 120, 120))
        self.fd_res_label.setPalette(self.fd_res_palette)
        self.fd_score_label.setText('-')
        self.fd_threshold_label.setText('-')

    def fault_detect_normal(self) -> None:
        self.fd_res_palette.setColor(QPalette.Window, QColor(60, 200, 120))
        self.fd_res_label.setText('NORMAL')
        self.fd_res_label.setPalette(self.fd_res_palette)

    def fault_detect_abnormal(self) -> None:
        self.fd_res_palette.setColor(QPalette.Window, QColor(255, 60, 60))
        self.fd_res_label.setText('ABNORMAL')
        self.fd_res_label.setPalette(self.fd_res_palette)

    def set_machine(self, m_conf: MachineConfig) -> None:
        self._m_conf = m_conf
        self._set_control_layout()

    @QtCore.Slot(tuple)
    def event_handle(self, zipped_data: Tuple) -> None:
        event, data = zipped_data

        if event is MachineEvent.DataUpdate:
            self.e_data_update(data)
        elif event is MachineEvent.FaultDetect:
            self.e_fault_detect(data)

    def e_data_update(self, named_data: Dict[str, List[float]]) -> None:
        for name, datas in named_data.items():
            if name in self.charts:
                if len(datas) > MAXIMUM_BATCH:
                    datas = signal.resample(datas, MAXIMUM_BATCH)
                self.charts[name].append_data(datas)

    def e_fault_detect(self, result: Dict[str, int]) -> None:
        self.fd_score_label.setText(f'{result["score"]}')
        self.fd_threshold_label.setText(f'{result["threshold"]}')

        if result["score"] > result["threshold"]:
            self.fault_detect_abnormal()
        else:
            self.fault_detect_normal()

    def _open_folder(self):
        path = os.path.join(self._m_conf.DATA_SAVE_MODE.PATH, self._m_conf.NAME)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
