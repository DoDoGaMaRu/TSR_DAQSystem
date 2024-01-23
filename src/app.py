from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from background import DAQSystem
from config import ConfigLoader
from config.paths import ICON_IMG
from gui.main_window import MainWindow
from gui.setting.setting_widget import QSettingWidget
from gui.startup import QStartupWidget
from gui.tray_icon import TrayIcon
from gui.running.daq_system_monitor import QDAQSystemMonitor


class App:
    def __init__(self):
        self._app = QApplication([])
        self._app.setQuitOnLastWindowClosed(False)

        self._bg_system: DAQSystem = None

        self._main_window = MainWindow(None)
        self.startup_step()

        icon = QIcon(ICON_IMG)
        self._tray = TrayIcon(main_window=self._main_window, icon=icon)
        self._tray.set_exit_event(self.exit_event)

    def startup_step(self) -> None:
        startup_widget = QStartupWidget(set_step=self.setting_step,
                                        run_step=self.running_step)
        self._main_window.setCentralWidget(startup_widget)

    def setting_step(self) -> None:
        setting_widget = QSettingWidget()
        setting_widget.setting_end.connect(self.startup_step)
        self._main_window.setCentralWidget(setting_widget)

    def running_step(self) -> None:
        conf = ConfigLoader.load_conf()
        self._bg_system = DAQSystem(conf)
        self._bg_system.start()

        machine_monitor = QDAQSystemMonitor(self._bg_system)
        self._main_window.setCentralWidget(machine_monitor)

    def run(self) -> None:
        self._app.exec()

    def exit_event(self) -> None:
        if self._bg_system is not None:
            self._bg_system.stop()
        self._app.exit()
