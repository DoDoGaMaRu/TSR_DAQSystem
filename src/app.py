from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from background import DAQSystem
from config import ConfigLoader
from config.paths import ICON_IMG
from gui.main_window import MainWindow
from gui.startup import QStartup
from gui.tray_icon import TrayIcon
from gui.running.daq_system_monitor import QDAQSystemMonitor


class App:
    def __init__(self):
        self._app = QApplication([])
        self._app.setQuitOnLastWindowClosed(False)

        self._machine_monitor = None
        self._bg_system: DAQSystem = None

        self._startup_widget = QStartup(set_step=self.setting_step,
                                        run_step=self.running_step)
        self._main_window = MainWindow(self._startup_widget)

        icon = QIcon(ICON_IMG)
        self._tray = TrayIcon(main_window=self._main_window, icon=icon)
        self._tray.set_exit_event(self.exit_event)

    def setting_step(self) -> None:
        pass

    def running_step(self) -> None:
        if self._bg_system is not None:
            self._bg_system.stop()

        conf = ConfigLoader.load_conf()
        self._bg_system = DAQSystem(conf)
        self._bg_system.start()

        self._machine_monitor = QDAQSystemMonitor(self._bg_system)
        self._main_window.setCentralWidget(self._machine_monitor)

    def run(self) -> None:
        self._app.exec()

    def exit_event(self) -> None:
        if self._bg_system is not None:
            self._bg_system.stop()
        self._app.exit()
