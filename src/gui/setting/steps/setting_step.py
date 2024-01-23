from abc import abstractmethod

from PySide6.QtWidgets import QWidget


class QSettingStep(QWidget):
    @abstractmethod
    def valid_check(self) -> bool:
        pass
