# -*- coding: utf-8 -*-

from collections import namedtuple
from . import codes
from . import utils


ArchiveProperties = namedtuple('ArchiveProperties',
                               'key start_time end_time')


Limits = namedtuple('Limits', 'low high')


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
                 alarm_limits=None, display_precision=None, archive_key=None,
                 interpolation=None):

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
        self.interpolation = interpolation

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
                     'archive_key', 'interpolation']:
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
