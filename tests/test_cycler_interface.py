import pytest
from pyctiarbin import CyclerInterface
from pyctiarbin.arbinspoofer import ArbinSpoofer
from pyctiarbin.messages import Msg

ARBIN_CHANNEL = 1

SPOOFER_CONFIG_DICT = {"ip": "127.0.0.1",
                       "port": 8956,
                       "num_channels": 16}

CYCLER_INTERFACE_CONFIG = {
    "ip_address": SPOOFER_CONFIG_DICT['ip'],
    "port": SPOOFER_CONFIG_DICT['port'],
    "timeout_s": 3,
    "msg_buffer_size": 2**12
}

ARBIN_SPOOFER = ArbinSpoofer(SPOOFER_CONFIG_DICT)
ARBIN_SPOOFER.start()


@pytest.mark.cycler_interface
def test_get_num_channels():
    """
    Test that sending the channel info message works correctly.
    """
    arbin_interface = CyclerInterface(CYCLER_INTERFACE_CONFIG)
    assert (arbin_interface.get_num_channels() == 16)


@pytest.mark.cycler_interface
def test_read_channel_status():
    """
    Test that sending the channel info message works correctly.
    """
    arbin_interface = CyclerInterface(CYCLER_INTERFACE_CONFIG)
    channel_status = arbin_interface.read_channel_status(
        channel=(ARBIN_CHANNEL+1))

    print(arbin_interface.get_num_channels())

    channel_status_bin_key = Msg.ChannelInfo.Server.pack({'channel': 1})
    channel_status_key = Msg.ChannelInfo.Server.unpack(channel_status_bin_key)
    assert (channel_status == channel_status_key)


@pytest.mark.cycler_interface
def test_read_all_channels_status():
    """
    Test that sending the channel info message works correctly.
    """
    arbin_interface = CyclerInterface(CYCLER_INTERFACE_CONFIG)
    channels_common_status, channels_status = arbin_interface.read_all_channels_status()

    channels_common_status_bin_key = Msg.ChannelsCommonInfo.Server.pack()
    channels_common_status_key = Msg.ChannelsCommonInfo.Server.unpack(
        channels_common_status_bin_key)

    channels_status_bin_key = Msg.ChannelsInfo.Server.pack(
        {"channel": SPOOFER_CONFIG_DICT["num_channels"]-1})
    channels_status_key = Msg.ChannelsInfo.Server.unpack(
        channels_status_bin_key)

    # Note:
    # 1. `msg_length` is only retrieved in `ChannelsCommonInfo`.
    # 2. `msg_length` is slightly larger(+2) than the sum of:
    #    - The length of the info shared by channels (24)
    #    - The message length for each channel multiplied by the number of channels.
    # 3. `msg_length` is asserted against the length of `msg_bin` in `unpackByTemplates`.
    if "msg_length" in channels_common_status:
        del channels_common_status["msg_length"]
    if "msg_length" in channels_common_status_key:
        del channels_common_status_key["msg_length"]

    assert (channels_common_status == channels_common_status_key)
    assert (channels_status == channels_status_key)
