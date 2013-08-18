#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
import datetime
from charc import utils

class AEST(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=10)

    def dst(self, dt):
        return datetime.timedelta(0)


class TestUtilFunctions(unittest.TestCase):

    def test_datetime_from_seconds_and_nanoseconds(self):
        seconds = 1376706013
        nanoseconds = 123456789
        dt = utils.datetime_from_seconds_and_nanoseconds(seconds, nanoseconds)
        # Note nanoseconds get rounded off in conversion to microseconds
        self.assertEqual(dt, datetime.datetime(2013, 8, 17, 2, 20, 13, 123457, utils.UTC()))

    def test_datetime_from_seconds_and_nanoseconds_with_tz(self):
        seconds = 1376706013
        nanoseconds = 123456789
        tz = AEST()
        dt = utils.datetime_from_seconds_and_nanoseconds(seconds, nanoseconds, tz)
        self.assertEqual(dt, datetime.datetime(2013, 8, 17, 12, 20, 13, 123457, AEST()))
        
    def test_seconds_and_nanoseconds_from_datetime(self):
        dt = datetime.datetime(2013, 8, 17, 2, 20, 13, 123456)
        seconds, nanoseconds = utils.seconds_and_nanoseconds_from_datetime(dt)
        self.assertEqual(seconds, 1376706013)
        self.assertEqual(nanoseconds, 123456000)

    def test_seconds_and_nanoseconds_from_datetime_with_tz(self):
        dt = datetime.datetime(2013, 8, 17, 12, 20, 13, 123456, AEST())
        seconds, nanoseconds = utils.seconds_and_nanoseconds_from_datetime(dt)
        self.assertEqual(seconds, 1376706013)
        self.assertEqual(nanoseconds, 123456000)

    def test_overlap_between_datetime_ranges(self):
        first_range_start = datetime.datetime(2013, 8, 17, 2, 20, 13, 123456)
        second_range_start = first_range_start + datetime.timedelta(hours=1)
        second_range_end = first_range_start + datetime.timedelta(hours=2)
        first_range_end = first_range_start + datetime.timedelta(hours=3)

        overlap = utils.overlap_between_datetime_ranges(first_range_start,
                                                        first_range_end,
                                                        second_range_start,
                                                        second_range_end)
        self.assertEqual(overlap, datetime.timedelta(hours=1))

    def test_overlap_between_datetime_ranges_with_tz(self):
        first_range_start = datetime.datetime(2013, 8, 17, 2, 20, 13, 123456, utils.UTC())
        second_range_start = first_range_start + datetime.timedelta(hours=1)
        second_range_end = first_range_start + datetime.timedelta(hours=2)
        first_range_end = first_range_start + datetime.timedelta(hours=3)

        second_range_start = second_range_start.astimezone(AEST())
        second_range_end = second_range_end.astimezone(AEST())

        overlap = utils.overlap_between_datetime_ranges(first_range_start,
                                                        first_range_end,
                                                        second_range_start,
                                                        second_range_end)

        self.assertEqual(overlap, datetime.timedelta(hours=1))

    def test_overlap_between_datetime_ranges_no_union(self):
        first_range_start = datetime.datetime(2013, 8, 17, 2, 20, 13, 123456)
        first_range_end = first_range_start + datetime.timedelta(hours=1)
        second_range_start = first_range_start + datetime.timedelta(hours=2)
        second_range_end = first_range_start + datetime.timedelta(hours=3)

        overlap = utils.overlap_between_datetime_ranges(first_range_start,
                                                        first_range_end,
                                                        second_range_start,
                                                        second_range_end)
        self.assertEqual(overlap, datetime.timedelta(0))

    def test_overlap_between_datetime_ranges_no_subset(self):
        first_range_start = datetime.datetime(2013, 8, 17, 2, 20, 13, 123456)
        second_range_start = first_range_start + datetime.timedelta(hours=1)
        first_range_end = first_range_start + datetime.timedelta(hours=2)
        second_range_end = first_range_start + datetime.timedelta(hours=3)

        overlap = utils.overlap_between_datetime_ranges(first_range_start,
                                                        first_range_end,
                                                        second_range_start,
                                                        second_range_end)
        self.assertEqual(overlap, datetime.timedelta(hours=1))

if __name__ == '__main__':
    unittest.main()
