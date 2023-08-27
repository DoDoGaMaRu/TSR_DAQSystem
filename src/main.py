import asyncio
from daq_system import DAQSystem


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    daq_system = DAQSystem()
    daq_system.run()

    loop.run_forever()
