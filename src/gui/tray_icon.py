import sys
from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QMainWindow


class TrayIcon(QSystemTrayIcon):
    def __init__(self, main_window: QMainWindow, icon: QIcon = None):
        super().__init__()
        if icon is not None:
            self.setIcon(icon)

        self._main_window = main_window
        self.activated.connect(self._tray_activated)

        self.exit_handler = sys.exit

        menu = QMenu()
        exit_action = menu.addAction("quit")
        exit_action.triggered.connect(self._exit_event)

        self.setContextMenu(menu)
        self.show()
        self.setToolTip("icon hover event")
        self.showMessage("DAQSystem", "System Started")

    def _exit_event(self):
        self.exit_handler()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            self._main_window.activateWindow() if self._main_window.isVisible() else self._main_window.show()

    def set_exit_event(self, handler: Callable):
        self.exit_handler = handler
