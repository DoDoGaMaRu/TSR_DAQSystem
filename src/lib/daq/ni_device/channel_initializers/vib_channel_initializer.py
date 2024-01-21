import nidaqmx
from nidaqmx.constants import ExcitationSource

from .channel_initializer import ChannelInitializer


class VibChannelInitializer(ChannelInitializer):
    def add_channel(self, task: nidaqmx.Task, physical_channel: str, **kwargs) -> None:
        task.ai_channels.add_ai_accel_chan(physical_channel, **kwargs,
                                           current_excit_source=ExcitationSource.INTERNAL)
