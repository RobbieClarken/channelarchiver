#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
import datetime
from charc import utils

class TestUtilFunctions(unittest.TestCase):

    def test_datetime_for_seconds_and_nanoseconds(self):
        seconds = 1376706013
        nanoseconds = 123456789
        dt = utils.datetime_for_seconds_and_nanoseconds(seconds, nanoseconds)
        # Note nanoseconds get rounded off in conversion to microseconds
        self.assertEqual(dt, datetime.datetime(2013, 8, 17, 2, 20, 13, 123457))

if __name__ == '__main__':
    unittest.main()
