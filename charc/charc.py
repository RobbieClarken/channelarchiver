# -*- coding: utf-8 -*-

try:
    from xmlrpclib import Server
except ImportError: # Python 3
    from xmlrpc.client import Server

import collections
import itertools

from . import codes
from . import utils

try:
    StrType = basestring
except NameError: # Python 3
    StrType = str


ArchiveProperties = collections.namedtuple('ArchiveProperties', 'key start_time end_time')
ChannelLimits = collections.namedtuple('ChannelLimits', 'low high')


class ChannelData(object):

    def __init__(self, archive_key, archive_data, tz):
        super(ChannelData, self).__init__()
        self.archive_key = archive_key
        self.name = archive_data['name']
        self.data_type = archive_data['type']
        meta_data = archive_data['meta']
        if meta_data['type'] == 0:
            self.states = meta_data['states']
            self.display_limits = None
            self.alarm_limits = None
            self.warn_limits = None
            self.precision = None
            self.units = None
        else:
            self.states = None
            self.display_limits = ChannelLimits(meta_data['disp_low'], meta_data['disp_high'])
            self.alarm_limits = ChannelLimits(meta_data['alarm_low'], meta_data['alarm_high'])
            self.warn_limits = ChannelLimits(meta_data['warn_low'], meta_data['warn_high'])
            self.precision = meta_data['prec']
            self.units = meta_data['units']
            
        self.elements_per_sample = archive_data['count']
        status = []
        severity = []
        time = []
        values = []
        for sample in archive_data['values']:
            status.append(sample['stat'])
            severity.append(sample['sevr'])
            time.append(utils.datetime_from_seconds_and_nanoseconds(sample['secs'], sample['nano'], tz))
            values.append(sample['value'])
        self.status = status
        self.severity = severity
        self.time = time
        self.values = values


class Archiver(object):

    def __init__(self, host):
        super(Archiver, self).__init__()
        self.server = Server(host)
        self.archiver = self.server.archiver
        self.archives_for_name = collections.defaultdict(list)
    
    def scan_archives(self, channel_names=None):
        if channel_names is None:
            channel_names = []
        channel_name_pattern = '|'.join(channel_names)
        list_emptied_for_channel = collections.defaultdict(bool)
        for archive in self.archiver.archives():
            archive_key = archive['key']
            for archive_details in self.archiver.names(archive_key, channel_name_pattern):
                name = archive_details['name']
                start_time = utils.datetime_from_seconds_and_nanoseconds(archive_details['start_sec'], archive_details['start_nano'])
                end_time = utils.datetime_from_seconds_and_nanoseconds(archive_details['end_sec'], archive_details['end_nano'])
                archive_properties = ArchiveProperties(archive_key, start_time, end_time)
                if list_emptied_for_channel[name]:
                    self.archives_for_name[name].append(archive_properties)
                else:
                    self.archives_for_name[name][:] = [archive_properties]
                    list_emptied_for_channel[name] = True
    
    def get(self, channel_names, start_datetime, end_datetime, count=10000,
               interpolation=codes.interpolate.RAW, scan_archives=True,
               archive_keys=None, tz=None):
        
        received_str = isinstance(channel_names, StrType)
        if received_str:
            channel_names = [ channel_names ]
            if archive_keys is not None:
                archive_keys = [ archive_keys ]

        if tz is None:
            tz = utils.UTC()

        # Convert datetimes to seconds and nanoseconds for archiver request
        start_seconds, start_nanoseconds = utils.seconds_and_nanoseconds_from_datetime(start_datetime)
        end_seconds, end_nanoseconds = utils.seconds_and_nanoseconds_from_datetime(end_datetime)

        if scan_archives:
            self.scan_archives(channel_names)
        
        if archive_keys is None:
            names_for_key = collections.defaultdict(list)
            for channel_name in channel_names:
                greatest_overlap = None
                key_with_greatest_overlap = None
                if channel_name not in self.archives_for_name:
                    raise Exception('Channel {} not found in any archive.'.format(channel_name))
                for archive_key, archive_start_time, archive_end_time in self.archives_for_name[channel_name]:
                    overlap = utils.overlap_between_datetime_ranges(start_datetime, end_datetime, archive_start_time, archive_end_time)
                    if greatest_overlap is None or overlap > greatest_overlap:
                        key_with_greatest_overlap = archive_key
                        greatest_overlap = overlap
                names_for_key[key_with_greatest_overlap].append(channel_name)
        else:
            if len(channel_names) != len(archive_keys):
                    raise Exception('Number of archive keys ({}) must equal number of channels ({}).'.format(len(archive_keys), len(channel_names)))
            # Group by archive key so we can request multiple channels with a single query
            key_for_name = dict(zip(channel_names, archive_keys))
            sorted_channel_names = sorted(channel_names, key=key_for_name.__getitem__)
            names_for_key = dict([(key, list(value)) for key, value in itertools.groupby(sorted_channel_names, key=key_for_name.__getitem__)])
        
        return_data = [ None ] * len(channel_names)
        
        for archive_key, channels in names_for_key.iteritems():
            data = self.archiver.values(archive_key, channels, start_seconds, start_nanoseconds, end_seconds, end_nanoseconds, count, interpolation)
            for archive_data in data:
                channel_data = ChannelData(archive_key, archive_data, tz)
                return_data[channel_names.index(channel_data.name)] = channel_data

        return return_data if not received_str else return_data[0]
