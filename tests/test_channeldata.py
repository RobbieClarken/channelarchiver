#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from channelarchiver import codes, utils
from channelarchiver.models import ChannelData, Limits
import datetime

utc = utils.UTC()


class TestChannelData(unittest.TestCase):

    def setUp(self):

        values = [200.5, 199.9, 198.7, 196.1]
        times = [
            datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
            datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc)
        ]

        self.scalar_channel = ChannelData(channel='EXAMPLE:DOUBLE_SCALAR',
                                          values=values, times=times,
                                          statuses=[0, 6, 6, 5],
                                          severities=[0, 1, 1, 2],
                                          units='mA',
                                          states=None,
                                          data_type=codes.data_type.DOUBLE,
                                          elements=1,
                                          display_limits=Limits(0, 220),
                                          warn_limits=Limits(199, 210),
                                          alarm_limits=Limits(198, 220),
                                          display_precision=3,
                                          archive_key=1001)
        array_values = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                         15, 16, 17, 18, 19],
                        [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89,
                         88, 87, 86, 85, 84, 83, 82, 81]]
        tz = utils.UTC(10)
        array_times = [
            datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, tz),
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, tz)
        ]

        self.array_channel = ChannelData(channel='EXAMPLE:DOUBLE_SCALAR',
                                         values=array_values,
                                         times=array_times,
                                         statuses=[0, 6],
                                         severities=[0, 1],
                                         units='mA',
                                         states=None,
                                         data_type=codes.data_type.DOUBLE,
                                         elements=20,
                                         display_limits=Limits(0, 220),
                                         warn_limits=Limits(199, 210),
                                         alarm_limits=Limits(198, 220),
                                         display_precision=3,
                                         archive_key=1001)

    def test_get_properties(self):

        channel_data = self.scalar_channel

        self.assertEqual(channel_data.channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(channel_data.values, [200.5, 199.9, 198.7, 196.1])
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

        channel_data = self.scalar_channel
        expected_str = ('               time  value      status  severity\n'
                        '2012-07-12 21:47:23  200.5    NO_ALARM  NO_ALARM\n'
                        '2012-07-13 02:05:01  199.9   LOW_ALARM     MINOR\n'
                        '2012-07-13 07:19:31  198.7   LOW_ALARM     MINOR\n'
                        '2012-07-13 11:18:55  196.1  LOLO_ALARM     MAJOR')
        self.assertEqual(str(channel_data), expected_str)

    def test_array_str(self):

        channel_data = self.array_channel
        expected_str = (
            '               time                                value     status  severity\n'  # noqa
            '2012-07-12 21:47:23  [  0,   1,   2,   3,   4,   5,   6,   NO_ALARM  NO_ALARM\n'  # noqa
            '                        7,   8,   9,  10,  11,  12,  13,                     \n'  # noqa
            '                       14,  15,  16,  17,  18,  19]                          \n'  # noqa
            '2012-07-13 02:05:01  [100,  99,  98,  97,  96,  95,  94,  LOW_ALARM     MINOR\n'  # noqa
            '                       93,  92,  91,  90,  89,  88,  87,                     \n'  # noqa
            '                       86,  85,  84,  83,  82,  81]'
        )
        self.assertEqual(str(channel_data), expected_str)

if __name__ == '__main__':
    unittest.main()
