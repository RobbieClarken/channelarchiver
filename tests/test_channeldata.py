#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from channelarchiver import ChannelData, codes, utils
from channelarchiver.models import Limits
import datetime

utc = utils.UTC()


class TestChannelData(unittest.TestCase):

    def setUp(self):

        values = [ 200.5, 199.9, 198.7, 196.1 ]
        times = [
            datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
            datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc)
        ]

        channel_data = ChannelData(channel='EXAMPLE:DOUBLE_SCALAR',
                                   values=values, times=times,
                                   statuses=[0, 6, 6, 5],
                                   severities = [0, 1, 1, 2],
                                   units = 'mA',
                                   states = None,
                                   data_type = codes.data_type.DOUBLE,
                                   elements = 1,
                                   display_limits = Limits(0, 220),
                                   warn_limits = Limits(199, 210),
                                   alarm_limits = Limits(198, 220),
                                   display_precision = 3,
                                   archive_key = 1001)
        self.scalar_channel_data = channel_data
    
    def test_get_properties(self):

        channel_data = self.scalar_channel_data

        self.assertEqual(channel_data.channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(channel_data.values, [ 200.5, 199.9, 198.7, 196.1 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
            datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc)
        ])
        self.assertEqual(channel_data.statuses, [0, 6, 6, 5])
        self.assertEqual(channel_data.severities, [0, 1, 1, 2])
        self.assertEqual(channel_data.units, 'mA')
        self.assertEqual(channel_data.states, None)
        self.assertEqual(channel_data.data_type, codes.data_type.DOUBLE)
        self.assertEqual(channel_data.elements, 1)
        self.assertEqual(channel_data.display_limits, Limits(0, 220))
        self.assertEqual(channel_data.warn_limits, Limits(199, 210))
        self.assertEqual(channel_data.alarm_limits, Limits(198, 220))
        self.assertEqual(channel_data.display_precision, 3)
        self.assertEqual(channel_data.archive_key, 1001)

    def test_scalar_str(self):

        channel_data = self.scalar_channel_data
        self.assertEqual(str(channel_data),
                ('               time  value      status  severity\n'
                 '2012-07-12 21:47:23  200.5    NO_ALARM  NO_ALARM\n'
                 '2012-07-13 02:05:01  199.9   LOW_ALARM     MINOR\n'
                 '2012-07-13 07:19:31  198.7   LOW_ALARM     MINOR\n'
                 '2012-07-13 11:18:55  196.1  LOLO_ALARM     MAJOR'))


if __name__ == '__main__':
    unittest.main()
