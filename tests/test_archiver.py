#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from channelarchiver import Archiver,  codes, utils, exceptions
from channelarchiver.models import ChannelData, ArchiveProperties
from .mock_archiver import MockArchiver
import datetime

utc = utils.UTC()


class TestArchiver(unittest.TestCase):
    
    def setUp(self):
        self.archiver = Archiver('http://fake')
        self.archiver.archiver = MockArchiver()

    def test_scan_archives_all(self):
        self.archiver.scan_archives()
        archives_for_channel = self.archiver.archives_for_channel
        self.assertTrue('EXAMPLE:DOUBLE_SCALAR' in archives_for_channel)
        self.assertTrue('EXAMPLE:INT_WAVEFORM' in archives_for_channel)
        self.assertTrue('EXAMPLE:ENUM_SCALAR' in archives_for_channel)
        self.assertEqual(
            archives_for_channel,
            {
                'EXAMPLE:DOUBLE_SCALAR': [
                    ArchiveProperties(
                        key=1001,
                        start_time=datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, tzinfo=utc),
                        end_time=datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, tzinfo=utc)
                    )
                 ],
                 'EXAMPLE:INT_WAVEFORM': [
                     ArchiveProperties(
                         key=1001,
                         start_time=datetime.datetime(2012, 7, 12, 23, 14, 19, 129600, tzinfo=utc),
                         end_time=datetime.datetime(2012, 7, 13, 8, 26, 18, 558211, tzinfo=utc)
                     )
                 ],
                 'EXAMPLE:ENUM_SCALAR': [
                     ArchiveProperties(
                         key=1008,
                         start_time=datetime.datetime(2012, 7, 12, 22, 41, 10, 765676, tzinfo=utc),
                         end_time=datetime.datetime(2012, 7, 13, 9, 20, 23, 623789, tzinfo=utc)
                     )
                 ]
            }
        )

    def test_scan_archives_one(self):
        self.archiver.scan_archives('EXAMPLE:DOUBLE_SCALAR')
        archives_for_channel = self.archiver.archives_for_channel.keys()
        self.assertTrue('EXAMPLE:DOUBLE_SCALAR' in archives_for_channel)
        self.assertFalse('EXAMPLE:INT_WAVEFORM' in archives_for_channel)
        self.assertFalse('EXAMPLE:ENUM_SCALAR' in archives_for_channel)

    def test_scan_archives_list(self):
        self.archiver.scan_archives(['EXAMPLE:DOUBLE_SCALAR',
                                     'EXAMPLE:ENUM_SCALAR'])
        archives_for_channel = self.archiver.archives_for_channel.keys()
        self.assertTrue('EXAMPLE:DOUBLE_SCALAR' in archives_for_channel)
        self.assertFalse('EXAMPLE:INT_WAVEFORM' in archives_for_channel)
        self.assertTrue('EXAMPLE:ENUM_SCALAR' in archives_for_channel)

    def test_get_scalar(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        data = self.archiver.get(['EXAMPLE:DOUBLE_SCALAR'], start, end,
                                 interpolation=codes.interpolation.RAW)
        self.assertTrue(isinstance(data, list))
        channel_data = data[0]
        self.assertEqual(channel_data.channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(channel_data.data_type, codes.data_type.DOUBLE)
        self.assertEqual(channel_data.elements, 1)
        self.assertEqual(channel_data.values, [ 200.5, 199.9, 198.7, 196.1 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
            datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc)
        ])
        self.assertEqual(channel_data.statuses, [0, 6, 6, 5])
        self.assertEqual(channel_data.severities, [0, 1, 1, 2])
        self.assertEqual(repr(channel_data.times[0].tzinfo), 'UTC()')

    def test_get_scalar_str(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                        interpolation=codes.interpolation.RAW)
        self.assertTrue(isinstance(channel_data, ChannelData))
        self.assertEqual(channel_data.channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(channel_data.data_type, codes.data_type.DOUBLE)

    def test_get_scalar_in_tz(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                 interpolation=codes.interpolation.RAW,
                                 tz=utils.UTC(11.5))
        self.assertEqual(str(data.times[0].tzinfo), 'UTC+11:30')
        self.assertEqual(repr(data.times[0].tzinfo), 'UTC(+11.5)')

    def test_get_without_scan(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        self.assertRaises(exceptions.ChannelNotFound,
                          self.archiver.get, ['EXAMPLE:DOUBLE_SCALAR'],
                          start, end,
                          interpolation=codes.interpolation.RAW,
                          scan_archives=False)

    def test_get_with_restrictive_interval(self):
        start = datetime.datetime(2012, 7, 13)
        end = datetime.datetime(2012, 7, 13, 10)
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                         interpolation=codes.interpolation.RAW)
        self.assertEqual(channel_data.values, [ 199.9, 198.7 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc)
        ])

    def test_get_with_restrictive_interval_with_tzs(self):
        start = datetime.datetime(2012, 7, 13, 10, tzinfo=utils.UTC(10))
        end = datetime.datetime(2012, 7, 13, 20, tzinfo=utils.UTC(10))
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                         interpolation=codes.interpolation.RAW)
        self.assertEqual(channel_data.values, [ 199.9, 198.7 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc)
        ])
        self.assertEqual(repr(channel_data.times[0].tzinfo), 'UTC(+10)')

    def test_get_with_str_times(self):
        start = '2012-07-13 00:00:00'
        end = '2012-07-13 10:00:00'
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                         interpolation=codes.interpolation.RAW)
        self.assertEqual(channel_data.values, [ 199.9, 198.7 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc)
        ])

    def test_get_with_str_times_incl_tz(self):
        start = '2012-07-13 10:00:00+10:00'
        end = '2012-07-13 20:00:00+10:00'
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                         interpolation=codes.interpolation.RAW)
        self.assertEqual(channel_data.values, [ 199.9, 198.7 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
            datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc)
        ])
        self.assertEqual(repr(channel_data.times[0].tzinfo), 'UTC(+10)')

    def test_get_waveform(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        channel_data = self.archiver.get(
                            'EXAMPLE:INT_WAVEFORM', start, end,
                            interpolation=codes.interpolation.RAW)
        self.assertEqual(channel_data.channel, 'EXAMPLE:INT_WAVEFORM')
        self.assertEqual(channel_data.data_type, codes.data_type.INT)
        self.assertEqual(channel_data.elements, 3)
        self.assertEqual(channel_data.values, [
            [3, 5, 13],
            [2, 4, 11],
            [0, 7, 1]
        ])

    def test_get_enum(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        channel_data = self.archiver.get(
                            'EXAMPLE:ENUM_SCALAR', start, end,
                            interpolation=codes.interpolation.RAW)
        self.assertEqual(channel_data.channel, 'EXAMPLE:ENUM_SCALAR')
        self.assertEqual(channel_data.data_type, codes.data_type.ENUM)
        self.assertEqual(channel_data.values, [7, 1, 8])

    def test_get_multiple(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        data = self.archiver.get(
                ['EXAMPLE:DOUBLE_SCALAR',
                 'EXAMPLE:INT_WAVEFORM',
                 'EXAMPLE:ENUM_SCALAR'],
                start, end,
                interpolation=codes.interpolation.RAW)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data[0].channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(data[1].channel, 'EXAMPLE:INT_WAVEFORM')
        self.assertEqual(data[2].channel, 'EXAMPLE:ENUM_SCALAR')
        self.assertEqual(data[0].values, [ 200.5, 199.9, 198.7, 196.1 ])
        self.assertEqual(data[1].values, [[3, 5, 13],
                                          [2, 4, 11],
                                          [0, 7, 1]])
        self.assertEqual(data[2].values, [7, 1, 8])

    def test_get_with_wrong_number_of_keys(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        self.assertRaises(exceptions.ChannelKeyMismatch,
                          self.archiver.get,
                          [ 'EXAMPLE:DOUBLE_SCALAR' ],
                          start, end,
                          archive_keys=[1001, 1008],
                          interpolation=codes.interpolation.RAW)

if __name__ == '__main__':
    unittest.main()
