from netCDF4 import Dataset  # pylint: disable=no-name-in-module

from .databook_gc import (
    channel_correspondence,
    channel_description_gc,
    platform_origin_gridsat_gc,
)
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


def validate_platform(platform: str) -> None:
    # Validate platform parameter
    if platform not in platform_origin_gridsat_gc:
        allowed_platforms = ", ".join(platform_origin_gridsat_gc.keys())
        raise ValueError(
            f"Invalid 'platform': '{platform}'; "
            f"allowed platforms are: {allowed_platforms}"
        )
