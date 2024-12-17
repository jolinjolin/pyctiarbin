import logging
import os
import struct
import socket
from pydantic import BaseModel
from pydantic import field_validator
from .messages import Msg

from .cycler_interface import CyclerInterface

logger = logging.getLogger(__name__)


class ChannelsInterface(CyclerInterface):
    """
    Class for interfacing with Arbin battery cycler at an all-channels level.
    """

    def __init__(self, config: dict, env_path: str = os.path.join(os.getcwd(), '.env')):
        """
        Creates a class instance for interfacing with Arbin battery cycler at an all-channels level.

        Parameters
        ----------
        config : dict
            A configuration dictionary. Must contain the following keys:
                ip_address : str
                    The IP address of the Arbin host computer.
                port : int
                    The TCP port to communicate through.
                timeout_s : *optional* : float
                    How long to wait before timing out on TCP communication. Defaults to 3 seconds.
                msg_buffer_size : *optional* : int
                    How big of a message buffer to use for sending/receiving messages.
                    A minimum of 1024 bytes is recommended. Defaults to 4096 bytes.
        env_path : *optional* : str
            The path to the `.env` file containing the Arbin CTI username,`ARBIN_CTI_USERNAME`, and password, `ARBIN_CTI_PASSWORD`.
            Defaults to looking in the working directory.

        Attributes
        ----------
        channel : int
            channel must be 0 (subtract one from the channel must be -1) to retrieve info of all channels at once.
            See THIRD_PARTY_GET_CHANNELS_INFO/THIRD_PARTY_GET_CHANNELS_INFO_FEEDBACK in Arbin Docs for more info.
        """
        self.__config = ChannelsInterfaceConfig(**config)
        super().__init__(self.__config.model_dump(), env_path)
        self.__channel = 0

    def read_channel_status(self) -> dict:
        """
        Reads the channel status for the passed channel.

        Parameters
        ----------
        channel : int
            The channel to read the status for.

        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """
        channel_common_info_msg_rd_dict = {}
        channel_info_msg_rx_dicts = []

        if (self.__channel != 0):
            logger.error(f'Channel must be 0!')
            return channel_common_info_msg_rd_dict, channel_info_msg_rx_dicts

        try:
            # Subtract one from the channel value to account for zero indexing
            channel_info_msg_tx = Msg.ChannelsCommonInfo.Client.pack(
                {'channel': (self.__channel - 1)})
            response_msg_bin = self._send_receive_msg(
                channel_info_msg_tx)

            if response_msg_bin and len(
                    response_msg_bin) >= Msg.ChannelsCommonInfo.Server.msg_length:
                channel_common_info_msg_rd_dict = Msg.ChannelsCommonInfo.Server.unpack(
                    response_msg_bin)
                channel_info_msg_rx_dicts = Msg.ChannelsInfo.Server.unpack(
                    response_msg_bin[Msg.ChannelsCommonInfo.Server.msg_length:])
        except Exception as e:
            logger.error(
                f'Error reading statues of all channels', exc_info=True)
            logger.error(e)

        return channel_common_info_msg_rd_dict, channel_info_msg_rx_dicts


class ChannelsInterfaceConfig(BaseModel):
    '''
    Holds channel config information for the ChannelsInterface class.

    Parameters
    ----------
        ip_address : str
            The IP address of the Arbin host computer.
        port : int
            The TCP port to communicate through.
        timeout_s : float
            How long to wait before timing out on TCP communication. Defaults to 3 seconds.
        msg_buffer_size : int
            How big of a message buffer to use for sending/receiving messages.
            A minimum of 1024 bytes is recommended. Defaults to 4096 bytes.
    '''
    test_name: str = None
    schedule_name: str = None
    ip_address: str
    port: int
    timeout_s: float = 3.0
    msg_buffer_size: int = 4096
