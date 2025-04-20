from netCDF4 import Dataset  # pylint: disable=no-name-in-module

from .databook_gc import channel_correspondence, channel_description_gc
from .netcdf_platform import GSPlatformMetadata


def validate_channel(channel: str, record: Dataset) -> None:
    # Validate channel id
    if channel not in channel_description_gc:
        allowed_channels = ", ".join(channel_description_gc.keys())
        raise ValueError(
            f"Invalid 'channel': '{channel}'; "
            f"allowed channels are: {allowed_channels}"
        )

    # Validate channel availability for the current platform
    pinfo = GSPlatformMetadata(record)
    channel_correspondence_map = channel_correspondence[pinfo.origin]
    channel_orig = channel_correspondence_map[channel]

    if channel_orig == 0:
        raise ValueError(
            f"Channel '{channel}' is not available "
            f"for platform '{pinfo.platform}'"
        )
