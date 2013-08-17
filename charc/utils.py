# -*- coding: utf-8 -*-

import datetime
import calendar

def datetime_from_seconds_and_nanoseconds(seconds, nanoseconds=0.0):
    timestamp = seconds + 1.e-9 * nanoseconds
    return datetime.datetime.utcfromtimestamp(timestamp)


def seconds_and_nanoseconds_from_datetime(dt):
    seconds = int(calendar.timegm(dt.utctimetuple()))
    nanoseconds = int(dt.microsecond * 1e3)
    return seconds, nanoseconds


def overlap_between_datetime_ranges(first_range_start, first_range_end,
                                    second_range_start, second_range_end):
    latest_start = max(first_range_start, second_range_start)
    earliest_end = min(first_range_end, second_range_end)
    return max((earliest_end - latest_start).total_seconds(), 0.0)
