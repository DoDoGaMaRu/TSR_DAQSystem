import nidaqmx
from nidaqmx.constants import ExcitationSource, ResistanceConfiguration

from .channel_initializer import ChannelInitializer


class TempChannelInitializer(ChannelInitializer):
    def add_channel(self, task: nidaqmx.Task, physical_channel: str, **kwargs) -> None:
        task.ai_channels.add_ai_rtd_chan(physical_channel, **kwargs,
                                         resistance_config=ResistanceConfiguration.THREE_WIRE,
                                         current_excit_source=ExcitationSource.INTERNAL, current_excit_val=0.00100)
