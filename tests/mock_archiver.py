# -*- coding: utf-8 -*-

import os
import json
import re
try:
    from xmlrpclib import Fault, ProtocolError
except ImportError: # Python 3
    from xmlrpc.client import Fault, ProtocolError
from channelarchiver import codes, utils


tests_dir =  os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(tests_dir, 'data')

def read_data(filename):
    path = os.path.join(data_dir, filename + '.json')
    with open(path) as f:
        data = json.load(f)
    return data

def check_type(value, check_type, expected_name):
    if not isinstance(value, check_type):
        supplied_name = type(value).__name__.upper()
        raise Fault(codes.xmlrpc.TYPE,
            ('Value of type {0} supplied where type {1} was '
             'expected.').format(supplied_name, expected_name))

class MockArchiver(object):
    '''
    A mock class to simulate XML-RPC calls to a Channel Archiver.

    Loads data for a mock archiver with the following archives and
    channels:

    1001
        * EXAMPLE:DOUBLE_SCALAR
            - 2012-07-12 21:47:23.663999895: 200.5
            - 2012-07-13 02:05:01.443588732: 199.9
            - 2012-07-13 07:19:31.806097162: 198.7
            - 2012-07-13 11:18:55.671259311: 196.1
        * EXAMPLE:INT_WAVEFORM
            - 2012-07-12 23:14:19.129599795: [3, 5, 13]
            - 2012-07-13 01:31:52.557222630: [2, 4, 11]
            - 2012-07-13 08:26:18.558211062: [0, 7, 1]
    1008
        * EXAMPLE:ENUM_SCALAR
            - 2012-07-12 22:41:10.765675810: 7
            - 2012-07-13 03:15:42.414257465: 1
            - 2012-07-13 09:20:23.623788581: 8
    '''

    def __init__(self):
        self._archives = read_data('archives')
        self._info = read_data('info')

    def info(self):
        return self._info

    def archives(self):
        archives = []
        for key, archive_spec in self._archives.items():
            archives.append({
                'key': int(key),
                'name': archive_spec['name'],
                'path': archive_spec['path']
            })
        return archives

    def names(self, key, pattern):
        check_type(key, int, 'INT')
        check_type(pattern, utils.StrType, 'STRING')
        pattern = '.*{0}.*'.format(pattern)
        key = str(key)
        self._check_key(key)
        archive_data = self._archives[key]['data']
        regex = re.compile(pattern)
        return_data = []
        for channel, channel_data in archive_data.items():
            if regex.match(channel) is None:
                continue
            values = channel_data['values']
            first_value = values[0]
            last_value = values[-1]
            return_data.append({
                'name': channel,
                'start_sec': first_value['secs'],
                'start_nano': first_value['nano'],
                'end_sec': last_value['secs'],
                'end_nano': last_value['nano']
            })
        return return_data

    def values(self, key, channels, start_sec, start_nano,
               end_sec, end_nano, count, interpolation):
        check_type(key, int, 'INT')
        check_type(channels, (list, tuple), 'ARRAY')
        for value in [start_sec,
                      start_nano,
                      end_sec,
                      end_nano,
                      count,
                      interpolation]:
            if not isinstance(value, int):
                raise ProtocolError(
                    'cr01arc01/cgi-bin/ArchiveDataServer.cgi',
                    codes.xmlrpc.INTERNAL, 'Internal Server Error',
                    None)
        if not 0 <= interpolation <= 4:
            raise Fault(codes.archiver.ARGUMENT_ERROR,
                        'Invalid how={0}'.format(interpolation))
        if interpolation != 0:
            raise Exception('Only raw interpolation is supported by'
                            'MockArchiver.')
        key = str(key)
        self._check_key(key)
        archive_data = self._archives[key]['data']
        return_data = []

        start = start_sec + 1e-9 * start_nano
        end = end_sec + 1e-9 * end_nano

        for channel in channels:
            try:
                channel_data = archive_data[channel].copy()
                channel_values = channel_data['values']
                for index, value in enumerate(channel_values):
                   time = value['secs'] + 1e-9 * value['nano']
                   if not start <= time <= end:
                       channel_values.pop(index)
                del channel_values[count:]
            except KeyError:
                channel_data = {
                    'count': 1,
                    'meta': {
                        'alarm_high': 0.0,
                        'alarm_low': 0.0,
                        'disp_high': 10.0,
                        'disp_low': 0.0,
                        'prec': 1,
                        'type': 1,
                        'units': '<NO DATA>',
                        'warn_high': 0.0,
                        'warn_low': 0.0
                    },
                    'name': channel,
                    'type': 1,
                    'values': []
                }
            return_data.append(channel_data)
        return return_data

    def _check_key(self, key):
        if key not in self._archives:
            raise Fault(codes.archiver.NO_INDEX,
                "Invalid key {0}". format(key))

    def __getattr__(self, name):
        raise Fault(codes.xmlrpc.NO_SUCH_METHOD,
            "Method 'archiver.{0}' not defined". format(name))
