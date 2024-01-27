from typing import List

from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout


class QRealtimeChart(QWidget):
    def __init__(self, parent: QWidget, name: str, maximum_view: int):
        super().__init__(parent)
        self._idx = 0
        self.maximum_view = maximum_view

        # Creating QChart
        self.chart = QChart()
        self.series = QLineSeries()
        self.series.setName(name)
        self.chart.addSeries(self.series)

        # Setting X-axis
        self.axis_x = QValueAxis()
        self.axis_x.setVisible(False)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        # Setting Y-axis
        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.4f")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        # Creating QChartView
        self.chart_view = QChartView(self.chart)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.chart_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)

    def append_data(self, datas: List[float]):
        for y in datas:
            self._idx += 1
            self.series.append(self._idx, y)

            while self.maximum_view < self.series.count():
                self.series.remove(0)

            y_max = max(self.series.points(), key=lambda e: e.y()).y()
            y_min = min(self.series.points(), key=lambda e: e.y()).y()
            y_margin = (y_max - y_min) * 0.2

            self.axis_y.setRange(y_min - y_margin, y_max + y_margin)
            self.axis_x.setRange(self._idx - self.maximum_view + 1, self._idx)

        if self._idx > 100000:
            self.series.clear()
            self._idx = 0
