import pytest
from pyctiarbin import ChannelsInterface
from pyctiarbin.arbinspoofer import ArbinSpoofer
from pyctiarbin.messages import Msg

SPOOFER_CONFIG_DICT = {"ip": "127.0.0.1",
                       "port": 8956,
                       "num_channels": 16}

CHANNELS_INTERFACE_CONFIG = {
    "ip_address": SPOOFER_CONFIG_DICT['ip'],
    "port": SPOOFER_CONFIG_DICT['port'],
    "timeout_s": 6,
    "msg_buffer_size": 6**12
}

ARBIN_SPOOFER = ArbinSpoofer(SPOOFER_CONFIG_DICT)
ARBIN_SPOOFER.start()


@pytest.mark.channel_interface
def test_read_channel_status():
    """
    Test that sending the channel info message works correctly.
    """
    arbin_interface = ChannelsInterface(CHANNELS_INTERFACE_CONFIG)
    channels_common_status, channels_status = arbin_interface.read_channel_status()

    channels_common_status_bin_key = Msg.ChannelsCommonInfo.Server.pack()
    channels_common_status_key = Msg.ChannelsCommonInfo.Server.unpack(
        channels_common_status_bin_key)

    channels_status_bin_key = Msg.ChannelsInfo.Server.pack(
        {"channel": SPOOFER_CONFIG_DICT["num_channels"]-1})
    channels_status_key = Msg.ChannelsInfo.Server.unpack(
        channels_status_bin_key)

    # Note:
    # 1. `msg_length` is only retrieved in `ChannelsCommonInfo`.
    # 2. `msg_length` cannot be estimated ahead of time, as it is not a fixed value.
    #    It is calculated as the sum of:
    #    - The length of the info shared by channels (24)
    #    - The message length for each channel multiplied by the number of channels.
    # 3. `msg_length` is asserted against the length of `msg_bin` in `unpackByTemplates`.
    if "msg_length" in channels_common_status:
        del channels_common_status["msg_length"]
    if "msg_length" in channels_common_status_key:
        del channels_common_status_key["msg_length"]

    assert (channels_common_status == channels_common_status_key)
    assert (channels_status == channels_status_key)
