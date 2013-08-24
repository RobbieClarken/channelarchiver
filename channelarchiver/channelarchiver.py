# -*- coding: utf-8 -*-

try:
    from xmlrpclib import Server
except ImportError: # Python 3
    from xmlrpc.client import Server

from collections import defaultdict
from itertools import groupby

from . import codes
from . import utils
from .models import ArchiveProperties, Limits
from .exceptions import ChannelNotFound, ChannelKeyMismatch


class ChannelData(object):
    '''
    Container for archive data for a single channel.

    Fields:
    channel: The channel name.
    values: A list of channel values.
    times: A list of datetimes corresponding with the retrieved times.
    statuses: A list of status values corresponding with the retrieved
        times.
    severities: A list of severity values corresponding with the
        retrieved times.
    units: The units of the values.
    states: A list of strings describing the states a STRING or ENUM
        can have.
    data_type: The data type of the channel.
    elements: The number of elements per sample for waveform channels.
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

    def __init__(self, channel=None, values=None, times=None, statuses=None,
                 severities=None, units=None, states=None, data_type=None,
                 elements=None, display_limits=None, warn_limits=None,
                 alarm_limits=None, display_precision=None, archive_key=None):

        super(ChannelData, self).__init__()

        self.channel = channel
        self.values = values
        self.times = times
        self.statuses = statuses
        self.severities = severities
        self.units = units
        self.states = states
        self.data_type = data_type
        self.elements = elements
        self.display_limits = display_limits
        self.warn_limits = warn_limits
        self.alarm_limits = alarm_limits
        self.display_precision = display_precision
        self.archive_key = archive_key

    def load_archive_data(self, archive_data, tz):
        self.channel = archive_data['name']
        self.data_type = archive_data['type']
        self.elements = elements = archive_data['count']

        meta_data = archive_data['meta']
        if meta_data['type'] == 0:
            self.states = meta_data['states']
        else:
            self.display_limits = Limits(meta_data['disp_low'],
                                         meta_data['disp_high'])
            self.alarm_limits = Limits(meta_data['alarm_low'],
                                       meta_data['alarm_high'])
            self.warn_limits = Limits(meta_data['warn_low'],
                                      meta_data['warn_high'])
            self.display_precision = meta_data['prec']
            self.units = meta_data['units']

        statuses = []
        severities = []
        times = []
        values = []
        for sample in archive_data['values']:
            value = sample['value'][0] if elements == 1 else sample['value']
            values.append(value)
            statuses.append(sample['stat'])
            severities.append(sample['sevr'])
            times.append(utils.datetime_from_sec_and_nano(sample['secs'],
                                                         sample['nano'],
                                                         tz))
        self.statuses = statuses
        self.severities = severities
        self.times = times
        self.values = values

    def __repr__(self):

        if self.data_type == codes.data_type.DOUBLE:
            fmt = '{0:.6g}'
        else:
            fmt = '{0!r}'

        s = 'ChannelData(\n'
        if self.elements == 1:
            s += utils.pretty_list_repr(self.values, fmt,
                                        prefix='    values=')
        else:
            s += utils.pretty_waveform_repr(self.values, fmt,
                                            prefix='    values=')
        s += ',\n'
        for attr in ['times', 'statuses', 'severities', 'states']:
            value = self.__getattribute__(attr)
            if value is None:
                continue
            prefix = '    {0}='.format(attr)
            s += utils.pretty_list_repr(value, prefix=prefix)
            s += ',\n'
        for attr in ['units', 'data_type', 'elements', 'display_limits',
                     'warn_limits', 'alarm_limits', 'display_precision',
                     'archive_key']:
            value = self.__getattribute__(attr)
            if value is None:
                continue
            s += '    {0}={1!r},\n'.format(attr, value)
        s = s[:-2]
        s += '\n)'
        return s

    def __str__(self):
        times = ['time'] + [
                    dt.replace(microsecond=0)
                    .isoformat(' ').replace('+00:00', '')
                        for dt in self.times]
        statuses = ['status'] + \
                list(map(codes.status.str_value, self.statuses))
        severities = ['severity'] + \
                list(map(codes.severity.str_value, self.severities))
        times_len = max(map(len, times))
        statuses_len = max(map(len, statuses))
        severities_len = max(map(len, severities))
        s = ''
        value_format = '{0:.9g}'
        if self.elements == 1:
            values = ['value'] + list(map(value_format.format, self.values))
        else:
            len_for_values = 79 - times_len - statuses_len - severities_len - 6
            values = ['value']
            max_value_len = utils.max_value_len_in_waveform(self.values,
                                                            value_format)
            for value in self.values:
                formatted_value = utils.pretty_list_repr(
                                    value, value_format,
                                    max_line_len=len_for_values,
                                    min_value_len=max_value_len)
                values += formatted_value.split('\n')

        values_len = max(map(len, values))
        spec = ('{0:>' + str(times_len) + '}  '
                '{1:>' + str(values_len) + '}  '
                '{2:>' + str(statuses_len) + '}  '
                '{3:>' + str(severities_len) + '}\n')

        if self.elements == 1:
            for fields in zip(times, values, statuses, severities):
                s += spec.format(*fields)
        else:
            i = 0
            for line in values:
                if i == 0 or '[' in line:
                    s += spec.format(times[i], line, statuses[i], severities[i])
                    i += 1
                else:
                    s += spec.format('', line.ljust(values_len), '', '')
        return s.rstrip()


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
        self.archives_for_channel = defaultdict(list)
    
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
        elif isinstance(channels, utils.StrType):
            channels = [ channels ]

        channel_pattern = '|'.join(channels)
        list_emptied_for_channel = defaultdict(bool)
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
    
    def get(self, channels, start, end, limit=1000,
               interpolation=codes.interpolation.LINEAR,
               scan_archives=True, archive_keys=None, tz=None):
        '''
        Retrieves archived.

        channels: The channels to get data for. Can be a string or
            list of strings.
        start: Start time as a datetime or ISO 8601 formatted string.
            If no timezone is specified, assumes UTC.
        end: End time as a datetime or ISO 8601 formatted string.
        limit: (optional) Number of data points to aim to retrieve.
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
            in. If omitted, the timezone of start will be used.
        '''
        
        received_str = isinstance(channels, utils.StrType)
        if received_str:
            channels = [ channels ]
            if archive_keys is not None:
                archive_keys = [ archive_keys ]

        if isinstance(start, utils.StrType):
            start = utils.datetime_from_isoformat(start)
        if isinstance(end, utils.StrType):
            end = utils.datetime_from_isoformat(end)

        if tz is None:
            tz = start.tzinfo if start.tzinfo else utils.UTC()

        # Convert datetimes to seconds and nanoseconds for archiver request
        start_sec, start_nano = utils.sec_and_nano_from_datetime(start)
        end_sec, end_nano = utils.sec_and_nano_from_datetime(end)

        if scan_archives:
            self.scan_archives(channels)
        
        if archive_keys is None:
            channels_for_key = defaultdict(list)
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
            if len(channels) != len(archive_keys):
                raise ChannelKeyMismatch('Number of archive keys must '
                                         'equal number of channels.')
            key_for_channel = dict(zip(channels, archive_keys))
            group_func = key_for_channel.__getitem__
            sorted_channels = sorted(channels, key=group_func)
            group_by_iter = groupby(sorted_channels, key=group_func)
            channels_for_key = dict(
                    (key, list(value)) for key, value in group_by_iter
            )
        
        return_data = [ None ] * len(channels)
        
        for archive_key, channels_on_archive in channels_for_key.items():
            data = self.archiver.values(archive_key, channels_on_archive,
                                        start_sec, start_nano,
                                        end_sec, end_nano,
                                        limit, interpolation)
            for archive_data in data:
                channel_data = ChannelData(archive_key=archive_key)
                channel_data.load_archive_data(archive_data, tz)
                index = channels.index(channel_data.channel)
                return_data[index] = channel_data

        return return_data if not received_str else return_data[0]
