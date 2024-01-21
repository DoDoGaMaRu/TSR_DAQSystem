import weakref
from typing import List, Dict
from scipy import signal

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QStackedWidget, QTableWidget, QTableWidgetItem, \
    QHeaderView, QAbstractItemView

from background.machine import Machine, EventHandler
from background.machine.event import Event
from .realtime_chart import QRealtimeChart


MAXIMUM_VIEW = 400
MAXIMUM_BATCH = int(MAXIMUM_VIEW * 0.05)


class CommonMeta(type(QWidget), type(EventHandler)):
    pass


class QMachine(QWidget, EventHandler, metaclass=CommonMeta):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._machine: Machine = None
        self._proxy = weakref.proxy(self)
        self.charts: Dict[str, QRealtimeChart] = {}

        self.layout = QHBoxLayout(self)

        self.chart_layout = QVBoxLayout()
        self.control_layout = QVBoxLayout()

        self._init_chart_layout()
        self._init_control_layout()

        self.layout.addLayout(self.chart_layout, stretch=7)
        self.layout.addLayout(self.control_layout, stretch=2)

    def __del__(self):
        self.reset()

    def _init_chart_layout(self):
        self.chart_stack = QStackedWidget()
        self.chart_layout.addWidget(self.chart_stack)

    def _init_control_layout(self):
        # set default info
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 15, 0, 0)

        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(12)
        info_title = QLabel('Machine Info')
        info_title.setFont(h1_font)
        info_layout.addWidget(info_title)

        name_layout = QHBoxLayout()
        self.name_label = QLabel()
        name_layout.addWidget(QLabel('Name : '), stretch=1)
        name_layout.addWidget(self.name_label, stretch=1)
        info_layout.addLayout(name_layout)

        fd_info_layout = QHBoxLayout()
        self.fd_info_label = QLabel()
        fd_info_layout.addWidget(QLabel('Fault Detect : '), stretch=1)
        fd_info_layout.addWidget(self.fd_info_label, stretch=1)
        info_layout.addLayout(fd_info_layout)

        self.control_layout.addLayout(info_layout)

        # set sensor table
        sensor_table_title = QLabel('Sensors')
        sensor_table_title.setFont(h1_font)
        sensor_table_title.setContentsMargins(0, 20, 0, 0)
        self.sensor_table = QTableWidget()
        self.sensor_table.setColumnCount(1)
        self.sensor_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        resize = QHeaderView.ResizeMode.Stretch
        horizontal_header = self.sensor_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(resize)
        horizontal_header.hide()

        vertical_header = self.sensor_table.verticalHeader()
        vertical_header.setAutoScroll(True)
        vertical_header.hide()

        self.sensor_table.itemClicked.connect(lambda item: self.chart_stack.setCurrentIndex(item.row()))

        self.control_layout.addWidget(sensor_table_title)
        self.control_layout.addWidget(self.sensor_table)

        # set fault detect
        fault_detect_title = QLabel('Fault Detect')
        fault_detect_title.setFont(h1_font)
        fault_detect_title.setContentsMargins(0, 20, 0, 0)

        fd_font = QFont()
        fd_font.setBold(True)
        fd_font.setPointSize(14)
        self.fd_palette = QPalette()
        self.fd_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.fd_label = QLabel()
        self.fd_label.setFont(fd_font)
        self.fd_label.setFixedHeight(50)
        self.fd_label.setAutoFillBackground(True)
        self.fd_label.setPalette(self.fd_palette)
        self.fd_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        fd_layout = QHBoxLayout()
        self.fd_score_label = QLabel('0')
        self.fd_threshold_label = QLabel('0')
        fd_layout.addWidget(QLabel('score : '))
        fd_layout.addWidget(self.fd_score_label)
        fd_layout.addWidget(QLabel('threshold : '))
        fd_layout.addWidget(self.fd_threshold_label)
        fd_layout.setContentsMargins(0, 0, 0, 30)

        self.control_layout.addWidget(fault_detect_title)
        self.control_layout.addWidget(self.fd_label)
        self.control_layout.addLayout(fd_layout)

    def _set_control_layout(self):
        self.name_label.setText(self._machine.get_name())
        self.fd_info_label.setText(str(self._machine.is_fault_detectable()))

        sensors: List[str] = self._machine.get_sensors()
        self.sensor_table.setRowCount(len(sensors))
        for idx, sensor in enumerate(sensors):
            new_chart = QRealtimeChart(self, sensor, MAXIMUM_VIEW)
            table_item = QTableWidgetItem(sensor)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            self.sensor_table.setItem(idx, 0, table_item)
            self.chart_stack.addWidget(new_chart)
            self.charts[sensor] = new_chart

        self.fd_label.setText('DISABLE')
        self.fd_palette.setColor(QPalette.Window, QColor(90, 90, 90))
        self.fd_label.setPalette(self.fd_palette)

    def set_machine(self, machine: Machine):
        self.reset()
        self._machine = machine
        self._machine.register_handler(self._proxy)
        self._set_control_layout()

    @QtCore.Slot()
    async def event_handle(self, event: Event, data: any) -> None:
        if event is Event.DataUpdate:
            self.e_data_update(data)
        elif event is Event.FaultDetect:
            self.e_fault_detect(data)

    def e_fault_detect(self, result: Dict[str, int]):
        self.fd_score_label.setText(f'{result["score"]}')
        self.fd_threshold_label.setText(f'{result["threshold"]}')

        if result["score"] > result["threshold"]:
            self.fd_palette.setColor(QPalette.Window, QColor(60, 200, 120))
            self.fd_label.setText('NORMAL')
        else:
            self.fd_palette.setColor(QPalette.Window, QColor(255, 60, 60))
            self.fd_label.setText('ABNORMAL')
        self.fd_label.setPalette(self.fd_palette)

    def e_data_update(self, named_data: Dict[str, List[float]]):
        for name, datas in named_data.items():
            if name in self.charts:
                if len(datas) > MAXIMUM_BATCH:
                    datas = signal.resample(datas, MAXIMUM_BATCH)
                self.charts[name].append_data(datas)

    def reset(self):
        if self._machine is not None:
            self._machine.remove_handler(self._proxy)
            self._machine = None
        while self.chart_stack.count():
            widget = self.chart_stack.widget(0)
            if widget:
                widget.deleteLater()
                self.chart_stack.removeWidget(widget)
        self.charts = {}
