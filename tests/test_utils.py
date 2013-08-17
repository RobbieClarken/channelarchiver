#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
import datetime
from charc import utils

class TestUtilFunctions(unittest.TestCase):

    def test_datetime_from_seconds_and_nanoseconds(self):
        seconds = 1376706013
        nanoseconds = 123456789
        dt = utils.datetime_from_seconds_and_nanoseconds(seconds, nanoseconds)
        # Note nanoseconds get rounded off in conversion to microseconds
        self.assertEqual(dt, datetime.datetime(2013, 8, 17, 2, 20, 13, 123457))

    def test_seconds_and_nanoseconds_from_datetime(self):
        dt = datetime.datetime(2013, 8, 17, 2, 20, 13, 123456)
        seconds, nanoseconds = utils.seconds_and_nanoseconds_from_datetime(dt)
        self.assertEqual(seconds, 1376706013)
        self.assertEqual(nanoseconds, 123456000)

if __name__ == '__main__':
    unittest.main()
