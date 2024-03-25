import sys
from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QMainWindow

from config.properties import APPLICATION_NAME


class TrayIcon(QSystemTrayIcon):
    def __init__(self, main_window: QMainWindow, icon: QIcon = None):
        super().__init__()
        if icon is not None:
            self.setIcon(icon)

        self._main_window = main_window
        self.activated.connect(self._tray_activated)

        menu = QMenu()

        self.exit_handler = sys.exit
        exit_action = menu.addAction("Quit")
        exit_action.triggered.connect(self._exit_event)

        self.setContextMenu(menu)
        self.show()
        self.setToolTip(APPLICATION_NAME)
        self.showMessage(APPLICATION_NAME, "System Started")

    def _exit_event(self):
        self.exit_handler()

    def set_exit_event(self, handler: Callable) -> None:
        self.exit_handler = handler

    def _tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            self._main_window.activateWindow() if self._main_window.isVisible() else self._main_window.show()

