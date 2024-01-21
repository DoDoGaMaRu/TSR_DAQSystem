import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from background import DAQSystem
from config import ConfigLoader
from config.paths import ICON_PATH
from gui.main_window import MainWindow
from gui.tray_icon import TrayIcon
from gui.running.machine_monitor import QMachineMonitor


class App:
    def __init__(self):
        self._app = QApplication([])
        self._app.setQuitOnLastWindowClosed(False)

        conf = ConfigLoader.load_conf()
        self._bg_system = DAQSystem(conf)
        self._bg_system.start()

        self._machines = self._bg_system.get_machines()
        self._machine_monitor = QMachineMonitor(self._machines)
        self._main_window = MainWindow(self._machine_monitor)

        icon = QIcon(ICON_PATH)
        self._tray = TrayIcon(main_window=self._main_window, icon=icon)
        self._tray.set_exit_event(self.exit_event)

    def run(self):
        self._app.exec()

    def exit_event(self):
        # TODO 에러 핸들링하기
        self._tray.hide()
        self._bg_system.exit()
        sys.exit()
