from PySide6.QtWidgets import QVBoxLayout

from config import DAQSystemConfig
from .setting_step import QSettingStep


class QMachineSetter(QSettingStep):
    def __init__(self, conf: DAQSystemConfig):
        super().__init__()
        self._conf: DAQSystemConfig = conf

        self.layout = QVBoxLayout(self)

    def valid_check(self) -> bool:
        return True
