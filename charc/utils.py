# -*- coding: utf-8 -*-

import datetime
import calendar

class UTC(datetime.tzinfo):
    '''UTC timezone'''

    ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def dst(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return 'UTC'


def utc_if_no_tzinfo(dt):
    return dt.replace(tzinfo=UTC()) if dt.tzinfo is None else dt


def datetime_from_sec_and_nano(seconds, nanoseconds=0.0, tz=None):
    '''
    Convert seconds and nanoseconds since the Epoch into a datetime with given timezone.
    If tz is not specified, UTC will be used.
    Note: Some precision will be lost as datetimes only store microseconds.
    '''
    if tz is None:
        tz = UTC()
    timestamp = seconds + 1.e-9 * nanoseconds
    return datetime.datetime.fromtimestamp(timestamp, tz)


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
