# -*- coding: utf-8 -*-

import datetime
import calendar
import re

try:
    StrType = basestring
except NameError: # Python 3
    StrType = str

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY  = 24
SECONDS_PER_HOUR = MINUTES_PER_HOUR * SECONDS_PER_MINUTE
SECONDS_PER_DAY = HOURS_PER_DAY * SECONDS_PER_HOUR

class UTC(datetime.tzinfo):
    '''UTC timezone with optional offset.'''

    def __init__(self, offset=0):
        '''
        offset: Timezone offset in hours relative to UTC.
        '''

        self.offset = datetime.timedelta(hours=offset)

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt=None):
        total_seconds = SECONDS_PER_DAY * self.offset.days + self.offset.seconds
        if total_seconds == 0:
            return 'UTC'

        sign = '-' if total_seconds < 0 else '+'
        total_seconds = abs(total_seconds)
        components = {
            'sign': sign,
            'hours': int(total_seconds / SECONDS_PER_HOUR),
            'minutes': int((total_seconds % SECONDS_PER_HOUR)/SECONDS_PER_MINUTE),
            'seconds': total_seconds % SECONDS_PER_MINUTE
        }
        if components['seconds']:
            spec = 'UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
        else:
            spec = 'UTC{sign}{hours:02d}:{minutes:02d}'
        return spec.format(**components)

    def __repr__(self):
        total_hours = HOURS_PER_DAY * self.offset.days + \
                      float(self.offset.seconds) / SECONDS_PER_HOUR
        return 'UTC({0:.8g})'.format(total_hours) if total_hours else 'UTC()'


def utc_if_no_tzinfo(dt):
    return dt.replace(tzinfo=UTC()) if dt.tzinfo is None else dt


def datetime_from_sec_and_nano(seconds, nanoseconds=0, tz=None):
    '''
    Convert seconds and nanoseconds since the Epoch into a datetime with given timezone.
    If tz is not specified, UTC will be used.
    Note: Some precision will be lost as datetimes only store microseconds.
    '''
    if tz is None:
        tz = UTC()
    # We create the datetime in two steps to avoid the weird
    # microsecond rounding behaviour in Python 3.
    dt = datetime.datetime.fromtimestamp(seconds, tz)
    return dt.replace(microsecond=int(round(1.e-3 * nanoseconds)))


def sec_and_nano_from_datetime(dt):
    '''
    Convert a datetime to seconds and nanoseconds since the Epoch.
    '''
    seconds = int(calendar.timegm(dt.utctimetuple()))
    nanoseconds = int(dt.microsecond * 1e3)
    return seconds, nanoseconds


def overlap_between_intervals(first_range_start, first_range_end,
                                    second_range_start, second_range_end):

    first_range_start = utc_if_no_tzinfo(first_range_start)
    first_range_end = utc_if_no_tzinfo(first_range_end)
    second_range_start = utc_if_no_tzinfo(second_range_start)
    second_range_end = utc_if_no_tzinfo(second_range_end)

    latest_start = max(first_range_start, second_range_start)
    earliest_end = min(first_range_end, second_range_end)

    return max(earliest_end - latest_start, datetime.timedelta(0))


def pretty_list_repr(lst, value_format='{0!r}', max_line_len=79, prefix='',
                     min_value_len=0):
    lst = list(map(value_format.format, lst))
    values = len(lst)
    max_value_len = max(max(map(len, lst)), min_value_len)
    prefix_len = len(prefix)
    delim = ', '
    delim_len = len(delim)
    paren_len = 2
    chars_per_line = max_line_len + delim_len - prefix_len - paren_len
    chars_per_value = max_value_len + delim_len
    values_per_line = max(int(chars_per_line / chars_per_value), 1)
    lines = int(values / values_per_line)
    if values % values_per_line != 0:
        lines += 1
    space_spec = '{0:>' + str(max_value_len) + '}'
    start_space = ' ' * (prefix_len + 1)
    s = prefix
    for line in range(lines):
        offset = line * values_per_line
        line_lst = lst[offset:(offset+values_per_line)]
        s += '[' if line == 0 else start_space
        s += delim.join(map(space_spec.format, line_lst))
        s += ']' if line == lines - 1 else ',\n'
    return s


def pretty_waveform_repr(lst, value_format='{0!r}', max_line_len=79, prefix=''):
    max_value_len = 0
    for sub_lst in lst:
        sub_lst = map(value_format.format, sub_lst)
        sub_max_val_len = max(map(len, sub_lst))
        max_value_len = max(max_value_len, sub_max_val_len)
    s = ''
    for idx, sub_lst in enumerate(lst):
        p = prefix + '[' if idx == 0 else ' ' * (len(prefix) + 1)
        s += pretty_list_repr(sub_lst, value_format, max_line_len, p, max_value_len)
        s += ']' if idx == len(lst) - 1 else ',\n'
    return s
