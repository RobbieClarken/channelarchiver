# -*- coding: utf-8 -*-

import os
import json
import re
from xmlrpclib import Fault, ProtocolError
from charc import codes

tests_dir =  os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(tests_dir, 'data')

def read_data(filename):
    path = os.path.join(data_dir, filename + '.json')
    return json.loads(open(path).read())

def check_type(value, check_type, expected_name):
    if not isinstance(value, check_type):
        supplied_name = type(value).__name__.upper()
        raise Fault(codes.xmlrpc.TYPE,
            ('Value of type {0} supplied where type {1} was '
             'expected.').format(supplied_name, expected_name))

class MockArchiver(object):
    '''
    A mock class to simulate XML-RPC calls to a Channel Archiver.
    '''
    _archives = read_data('archives')
    _info = read_data('info')

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
        check_type(pattern, basestring, 'STRING')
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
        key = str(key)
        self._check_key(key)
        archive_data = self._archives[key]['data']
        return_data = []
        for channel in channels:
            try:
                channel_data = archive_data[channel]
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
