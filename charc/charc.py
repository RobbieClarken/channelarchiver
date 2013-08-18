# -*- coding: utf-8 -*-

try:
    from xmlrpclib import Server
except ImportError: # Python 3
    from xmlrpc.client import Server

import collections
from itertools import groupby

from . import codes
from . import utils
from .exceptions import ChannelNotFound, ChannelKeyMismatch

try:
    StrType = basestring
except NameError: # Python 3
    StrType = str


ArchiveProperties = collections.namedtuple('ArchiveProperties',
                                           'key start_time end_time')
ChannelLimits = collections.namedtuple('ChannelLimits', 'low high')


class ChannelData(object):
    '''
    Container for archive data for a single channel.

    Fields:
    channel: The channel name.
    values: A list of channel values.
    time: A list of datetimes corresponding with the retrieved times.
    status: A list of status values corresponding with the retrieved
        times.
    severity: A list of severity values corresponding with the
        retrieved times.
    units: The units of the values.
    states: A list of strings describing the states a STRING or ENUM
        can have.
    data_type: The data type of the channel.
    display_limits: Values advising how to display the values in a user
        interface.
    warn_limits: Low and high values for which the channel will
        generate a warning.
    alarm_limits: Low and high values for which the channel will
        generate an alarm.
    display_precision: The number of decimal places to show in user
        interfaces.
    archive_key: The archive the data was pulled from.
    '''

    def __init__(self, archive_key, archive_data, tz):

        super(ChannelData, self).__init__()

        self.archive_key = archive_key
        self.channel = archive_data['name']
        self.data_type = archive_data['type']
        self.elements_per_sample = archive_data['count']

        meta_data = archive_data['meta']
        if meta_data['type'] == 0:
            self.states = meta_data['states']
            self.display_limits = None
            self.alarm_limits = None
            self.warn_limits = None
            self.display_precision = None
            self.units = None
        else:
            self.states = None
            self.display_limits = ChannelLimits(meta_data['disp_low'],
                                                meta_data['disp_high'])
            self.alarm_limits = ChannelLimits(meta_data['alarm_low'],
                                              meta_data['alarm_high'])
            self.warn_limits = ChannelLimits(meta_data['warn_low'],
                                             meta_data['warn_high'])
            self.display_precision = meta_data['prec']
            self.units = meta_data['units']

        status = []
        severity = []
        time = []
        values = []
        for sample in archive_data['values']:
            status.append(sample['stat'])
            severity.append(sample['sevr'])
            time.append(utils.datetime_from_sec_and_nano(sample['secs'],
                                                         sample['nano'],
                                                         tz))
            values.append(sample['value'])
        self.status = status
        self.severity = severity
        self.time = time
        self.values = values


class Archiver(object):
    '''
    Class for interacting with an EPICS Channel Access Archiver.
    '''

    def __init__(self, host):
        '''
        host: The URL of your archiver's ArchiveDataServer.cgi. Will
            look something like:
            http://cr01arc01/cgi-bin/ArchiveDataServer.cgi
        '''

        super(Archiver, self).__init__()
        self.server = Server(host)
        self.archiver = self.server.archiver
        self.archives_for_channel = collections.defaultdict(list)
    
    def scan_archives(self, channels=None):
        '''
        Determine which archives contain the specified channels. This
        can be called prior to calling .get() with scan_archives=False
        to speed up data retrieval.
        
        channels: (optional) The channel names to scan for. Can be a
            string or list of strings.
            If omitted, all channels will be scanned for.
        '''

        if channels is None:
            channels = []
        elif isinstance(channels, StrType):
            channels = [ channels ]

        channel_pattern = '|'.join(channels)
        list_emptied_for_channel = collections.defaultdict(bool)
        for archive in self.archiver.archives():
            archive_key = archive['key']
            archives = self.archiver.names(archive_key, channel_pattern)
            for archive_details in archives:
                channel = archive_details['name']
                start_time = utils.datetime_from_sec_and_nano(
                        archive_details['start_sec'],
                        archive_details['start_nano'])
                end_time = utils.datetime_from_sec_and_nano(
                        archive_details['end_sec'],
                        archive_details['end_nano'])
                properties = ArchiveProperties(archive_key,
                                                       start_time,
                                                       end_time)
                if list_emptied_for_channel[channel]:
                    self.archives_for_channel[channel].append(properties)
                else:
                    self.archives_for_channel[channel][:] = [ properties ]
                    list_emptied_for_channel[channel] = True
    
    def get(self, channels, start, end, count=10000,
               interpolation=codes.interpolate.LINEAR,
               scan_archives=True, archive_keys=None, tz=None):
        '''
        Retrieves archived.

        channels: The channels to get data for. Can be a string or
            list of strings.
        start: Start time as a datetime. If no timezone is specified,
            assumes UTC.
        end: End time as a datetime.
        count: (optional) Number of data points to aim to retrieve.
            The actual number returned may differ depending on the
            number of points in the archive, the interpolation method
            and the maximum allowed points set by the archiver.
        interpolation: (optional) Method of interpolating the data.
            Should be one of RAW, SPREADSHEET, AVERAGED, PLOT_BINNING
            or LINEAR from the codes.interpolate object.
            Default: LINEAR
        scan_archives: (optional) Whether or not to perform a scan to
            determine which archives the channels are on. If this is to
            be False .scan_archives() should have been called prior to
            calling .get().
            Default: True
        archive_keys: (optional) The keys of the archives to get data
            from. Should be the same length as channels. If this
            is omitted the archives with the greatest coverage of the
            requested time interval will be used.
        tz: (optional) The timezone that datetimes should be returned
            in. If omitted, UTC will be used.
        '''
        
        received_str = isinstance(channels, StrType)
        if received_str:
            channels = [ channels ]
            if archive_keys is not None:
                archive_keys = [ archive_keys ]

        if tz is None:
            tz = utils.UTC()

        # Convert datetimes to seconds and nanoseconds for archiver request
        start_sec, start_nano = utils.sec_and_nano_from_datetime(start)
        end_sec, end_nano = utils.sec_and_nano_from_datetime(end)

        if scan_archives:
            self.scan_archives(channels)
        
        if archive_keys is None:
            channels_for_key = collections.defaultdict(list)
            for channel in channels:
                greatest_overlap = None
                key_with_greatest_overlap = None
                archives = self.archives_for_channel[channel]
                for archive_key, archive_start, archive_end in archives:
                    overlap = utils.overlap_between_intervals(start, end,
                                                              archive_start,
                                                              archive_end)
                    if greatest_overlap is None or overlap > greatest_overlap:
                        key_with_greatest_overlap = archive_key
                        greatest_overlap = overlap
                if key_with_greatest_overlap is None:
                    raise ChannelNotFound(('Channel {0} not found in '
                                           'any archive (an archive scan '
                                           'may be needed).').format(channel))
                channels_for_key[key_with_greatest_overlap].append(channel)
        else:
            # Group by archive key so we can request multiple channels
            # with a single query
            try:
                key_for_channel = dict(zip(channels, archive_keys))
                group_func = key_for_channel.__getitem__
                sorted_channels = sorted(channels, key=group_func)
                group_by_iter = groupby(sorted_channels, key=group_func)
                channels_for_key = dict(
                        (key, list(value)) for key, value in group_by_iter
                )
            except KeyError:
                raise ChannelKeyMismatch('Number of archive keys must '
                                         'equal number of channels.')
        
        return_data = [ None ] * len(channels)
        
        for archive_key, channels_on_archive in channels_for_key.iteritems():
            data = self.archiver.values(archive_key, channels,
                                        start_sec, start_nano,
                                        end_sec, end_nano,
                                        count, interpolation)
            for archive_data in data:
                channel_data = ChannelData(archive_key, archive_data, tz)
                index = channels.index(channel_data.channel)
                return_data[index] = channel_data

        return return_data if not received_str else return_data[0]
