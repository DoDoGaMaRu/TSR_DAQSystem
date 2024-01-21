import os
import shutil
from typing import List, Dict

from util.clock import get_date, get_time, TimeEvent
from config.paths import DATA_DIR
from lib.csv_writer import CsvWriter
from .machine import EventHandler
from .machine.event import Event


class DataSaver(EventHandler):
    def __init__(self,
                 name: str,
                 sensors: List[str],
                 external_path: str):
        self._save_path = os.path.join(DATA_DIR, name)
        self._sensors = sensors
        self._external_path = os.path.join(external_path, name)

        self._writers: Dict[str, CsvWriter] = {}
        self._time_event = TimeEvent()
        self._init_writers()

    def _init_writers(self):
        self._writers = {}

        os.makedirs(self._save_path, exist_ok=True)
        os.makedirs(self._external_path, exist_ok=True)
        for sensor in self._sensors:
            header: List[str] = ['time', 'data']
            path = os.path.join(self._save_path, make_file_name(sensor))
            self._writers[sensor] = CsvWriter(path, header)

    def _move_files(self):
        files = os.listdir(self._save_path)

        os.makedirs(self._external_path, exist_ok=True)
        for file_name in files:
            src_path = os.path.join(self._save_path, file_name)
            dest_path = os.path.join(self._external_path, file_name)
            shutil.move(src_path, dest_path)

    async def event_handle(self, event: Event, data: any) -> None:
        if event is Event.DataUpdate:
            if self._time_event.is_day_change():
                self._move_files()
                self._init_writers()

            cur_time = get_time()
            for sensor, datas in data.items():
                datas = [[cur_time, data] for data in datas]
                self._writers[sensor].add_datas(datas)


def make_file_name(name: str) -> str:
    return f'{get_date()}_{name}.csv'
