# -*- coding: utf-8 -*-

try:
    from xmlrpc.client import Server
except ImportError:  # Python 2
    from xmlrpclib import Server

from collections import defaultdict
from itertools import groupby

from . import codes
from . import utils
from .models import ChannelData, ArchiveProperties, Limits
from .exceptions import ChannelNotFound, ChannelKeyMismatch


class Archiver(object):
    """Class for interacting with an EPICS Channel Access Archiver."""

    def __init__(self, host):
        """
        Args:
            host (str): URL to your archiver's ArchiveDataServer.cgi. Will
                look something like: http://cr01arc01/cgi-bin/ArchiveDataServer.cgi

        """
        super(Archiver, self).__init__()
        self.server = Server(host)
        self.archiver = self.server.archiver
        self.archives_for_channel = defaultdict(list)

    def scan_archives(self, channels=None):
        """
        Determine which archives contain the specified channels. This
        can be called prior to calling .get() with scan_archives=False
        to speed up data retrieval.

        Args:
            channels (Optional[List[str]]): The channel names to scan for.
                If omitted, all channels will be scanned for.

        """

        if channels is None:
            channels = []
        elif isinstance(channels, utils.StrType):
            channels = [channels]

        channel_pattern = "|".join(channels)
        list_emptied_for_channel = defaultdict(bool)
        for archive in self.archiver.archives():
            archive_key = archive["key"]
            archives = self.archiver.names(archive_key, channel_pattern)
            for archive_details in archives:
                channel = archive_details["name"]
                start_time = utils.datetime_from_sec_and_nano(
                    archive_details["start_sec"],
                    archive_details["start_nano"],
                    utils.utc,
                )
                end_time = utils.datetime_from_sec_and_nano(
                    archive_details["end_sec"], archive_details["end_nano"], utils.utc
                )
                properties = ArchiveProperties(archive_key, start_time, end_time)
                if list_emptied_for_channel[channel]:
                    self.archives_for_channel[channel].append(properties)
                else:
                    self.archives_for_channel[channel][:] = [properties]
                    list_emptied_for_channel[channel] = True

    def _parse_values(self, archive_data, tz):
        channel_data = ChannelData(
            channel=archive_data["name"],
            data_type=archive_data["type"],
            elements=archive_data["count"],
        )

        meta_data = archive_data["meta"]
        if meta_data["type"] == 0:
            channel_data.states = meta_data["states"]
        else:
            channel_data.display_limits = Limits(
                meta_data["disp_low"], meta_data["disp_high"]
            )
            channel_data.alarm_limits = Limits(
                meta_data["alarm_low"], meta_data["alarm_high"]
            )
            channel_data.warn_limits = Limits(
                meta_data["warn_low"], meta_data["warn_high"]
            )
            channel_data.display_precision = meta_data["prec"]
            channel_data.units = meta_data["units"]

        statuses = []
        severities = []
        times = []
        values = []
        for sample in archive_data["values"]:
            if channel_data.elements == 1:
                values.append(sample["value"][0])
            else:
                values.append(sample["value"])
            statuses.append(sample["stat"])
            severities.append(sample["sevr"])
            times.append(
                utils.datetime_from_sec_and_nano(sample["secs"], sample["nano"], tz)
            )
        channel_data.values = values
        channel_data.times = times
        channel_data.statuses = statuses
        channel_data.severities = severities

        return channel_data

    def get(
        self,
        channels,
        start,
        end,
        limit=1000,
        interpolation="linear",
        scan_archives=True,
        archive_keys=None,
        tz=None,
    ):
        """
        Retrieves archived data.

        Args:
            channels (str or List[str]): The channels to get data for.
            start (str or datetime): Start time as a datetime or ISO 8601
                formatted string.  If no timezone is specified, assumes
                local timezone.
            end (str or datetime): End time.
            limit (Optional[int]): Number of data points to aim to retrieve.
                The actual number returned may differ depending on the
                number of points in the archive, the interpolation method
                and the maximum allowed points set by the archiver.
            interpolation (Optional[str]): Method of interpolating the data.
                Should be one of 'raw', 'spreadsheet', 'averaged',
                'plot-binning' or 'linear'.
            scan_archives (Optional[bool]): Whether or not to perform a scan to
                determine which archives the channels are on. If this is to
                be False .scan_archives() should have been called prior to
                calling .get().
                Default: True
            archive_keys (Optional[List[int]]): The keys of the archives to get
                data from. Should be the same length as channels. If this
                is omitted the archives with the greatest coverage of the
                requested time interval will be used.
            tz (Optional[tzinfo]): The timezone that datetimes should be returned
                in. If omitted, the timezone of start will be used.

        Returns:
            ChannelData objects. If the channels parameters was a string the
            returned value will be a single ChannelData object. If channels was a
            list of strings a list of ChannelData objects will be returned.

        """

        received_str = isinstance(channels, utils.StrType)
        if received_str:
            channels = [channels]
            if archive_keys is not None:
                archive_keys = [archive_keys]

        if isinstance(start, utils.StrType):
            start = utils.datetime_from_isoformat(start)
        if isinstance(end, utils.StrType):
            end = utils.datetime_from_isoformat(end)
        if isinstance(interpolation, utils.StrType):
            interpolation = codes.interpolation[interpolation]

        if start.tzinfo is None:
            start = utils.localize_datetime(start, utils.local_tz)

        if end.tzinfo is None:
            end = utils.localize_datetime(end, utils.local_tz)

        if tz is None:
            tz = start.tzinfo

        # Convert datetimes to seconds and nanoseconds for archiver request
        start_sec, start_nano = utils.sec_and_nano_from_datetime(start)
        end_sec, end_nano = utils.sec_and_nano_from_datetime(end)

        if archive_keys is None:
            if scan_archives:
                self.scan_archives(channels)
            channels_for_key = defaultdict(list)
            for channel in channels:
                greatest_overlap = None
                key_with_greatest_overlap = None
                archives = self.archives_for_channel[channel]
                for archive_key, archive_start, archive_end in archives:
                    overlap = utils.overlap_between_intervals(
                        start, end, archive_start, archive_end
                    )
                    if greatest_overlap is None or overlap > greatest_overlap:
                        key_with_greatest_overlap = archive_key
                        greatest_overlap = overlap
                if key_with_greatest_overlap is None:
                    raise ChannelNotFound(
                        f"Channel {channel} not found in any archive (a scan may be needed)"
                    )
                channels_for_key[key_with_greatest_overlap].append(channel)
        else:
            # Group by archive key so we can request multiple channels
            # with a single query
            if len(channels) != len(archive_keys):
                raise ChannelKeyMismatch(
                    "Number of archive keys must equal number of channels."
                )
            key_for_channel = dict(zip(channels, archive_keys))
            grouping_func = key_for_channel.get
            groups = groupby(sorted(channels, key=grouping_func), key=grouping_func)
            channels_for_key = {key: list(channels) for key, channels in groups}

        return_data = [None] * len(channels)

        for archive_key, channels_on_archive in channels_for_key.items():
            data = self.archiver.values(
                archive_key,
                channels_on_archive,
                start_sec,
                start_nano,
                end_sec,
                end_nano,
                limit,
                interpolation,
            )
            for archive_data in data:
                channel_data = self._parse_values(archive_data, tz)
                channel_data.archive_key = archive_key
                channel_data.interpolation = interpolation
                index = channels.index(channel_data.channel)
                return_data[index] = channel_data

        return return_data if not received_str else return_data[0]
