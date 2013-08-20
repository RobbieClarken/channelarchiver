#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from channelarchiver import Archiver, ChannelData, codes, utils, exceptions
from mock_archiver import MockArchiver
import datetime

utc = utils.UTC()


class TestArchiver(unittest.TestCase):
    
    def setUp(self):
        self.archiver = Archiver('http://fake')
        self.archiver.archiver = MockArchiver()

    def test_scan_archives_all(self):
        self.archiver.scan_archives()
        channels_found = self.archiver.archives_for_channel.keys()
        self.assertTrue('EXAMPLE:DOUBLE_SCALAR' in channels_found)
        self.assertTrue('EXAMPLE:INT_WAVEFORM' in channels_found)
        self.assertTrue('EXAMPLE:ENUM_SCALAR' in channels_found)

    def test_scan_archives_one(self):
        self.archiver.scan_archives('EXAMPLE:DOUBLE_SCALAR')
        channels_found = self.archiver.archives_for_channel.keys()
        self.assertTrue('EXAMPLE:DOUBLE_SCALAR' in channels_found)
        self.assertFalse('EXAMPLE:INT_WAVEFORM' in channels_found)
        self.assertFalse('EXAMPLE:ENUM_SCALAR' in channels_found)

    def test_scan_archives_list(self):
        self.archiver.scan_archives(['EXAMPLE:DOUBLE_SCALAR',
                                     'EXAMPLE:ENUM_SCALAR'])
        channels_found = self.archiver.archives_for_channel.keys()
        self.assertTrue('EXAMPLE:DOUBLE_SCALAR' in channels_found)
        self.assertFalse('EXAMPLE:INT_WAVEFORM' in channels_found)
        self.assertTrue('EXAMPLE:ENUM_SCALAR' in channels_found)

    def test_get_scalar(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        data = self.archiver.get(['EXAMPLE:DOUBLE_SCALAR'], start, end,
                                 interpolation=codes.interpolate.RAW)
        self.assertTrue(isinstance(data, list))
        channel_data = data[0]
        self.assertEqual(channel_data.channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(channel_data.data_type, codes.data_type.DOUBLE)
        self.assertEqual(channel_data.elements, 1)
        self.assertEqual(channel_data.values, [ 200.5, 199.9, 198.7, 196.1 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
            datetime.datetime(2012, 7, 13, 02, 05, 01, 443589, utc),
            datetime.datetime(2012, 7, 13, 07, 19, 31, 806097, utc),
            datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc)
        ])

    def test_get_scalar_str(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                        interpolation=codes.interpolate.RAW)
        self.assertTrue(isinstance(channel_data, ChannelData))
        self.assertEqual(channel_data.channel, 'EXAMPLE:DOUBLE_SCALAR')
        self.assertEqual(channel_data.data_type, codes.data_type.DOUBLE)

    def test_get_without_scan(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        with self.assertRaises(exceptions.ChannelNotFound):
            data = self.archiver.get(['EXAMPLE:DOUBLE_SCALAR'], start, end,
                                     interpolation=codes.interpolate.RAW,
                                     scan_archives=False)

    def test_get_with_restrictive_interval(self):
        start = datetime.datetime(2012, 7, 13)
        end = datetime.datetime(2012, 7, 13, 10)
        channel_data = self.archiver.get('EXAMPLE:DOUBLE_SCALAR', start, end,
                                         interpolation=codes.interpolate.RAW)
        self.assertEqual(channel_data.values, [ 199.9, 198.7 ])
        self.assertEqual(channel_data.times, [
            datetime.datetime(2012, 7, 13, 02, 05, 01, 443589, utc),
            datetime.datetime(2012, 7, 13, 07, 19, 31, 806097, utc)
        ])

    def test_get_waveform(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2013, 1, 1)
        channel_data = self.archiver.get(
                            'EXAMPLE:INT_WAVEFORM', start, end,
                            interpolation=codes.interpolate.RAW)
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
                            interpolation=codes.interpolate.RAW)
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
                interpolation=codes.interpolate.RAW)
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
        with self.assertRaises(exceptions.ChannelKeyMismatch):
            self.archiver.get(
                [ 'EXAMPLE:DOUBLE_SCALAR' ],
                start, end,
                archive_keys=[1001, 1008],
                interpolation=codes.interpolate.RAW)

if __name__ == '__main__':
    unittest.main()
