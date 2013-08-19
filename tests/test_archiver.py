#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from charc import Archiver
from mock_archiver import MockArchiver


class TestArchiver(unittest.TestCase):
    
    def setUp(self):
        self.archiver = Archiver('http://fake')
        self.archiver.archiver = MockArchiver()

    def test_scan_archives_all(self):
        self.archiver.scan_archives()
        channels_found = self.archiver.archives_for_channel.keys()
        self.assertTrue('SR11BCM01:CURRENT_MONITOR' in channels_found)
        self.assertTrue('SR11BCM01:LIFETIME_MONITOR' in channels_found)
        self.assertTrue('TS01FPC01:FILL_CMD' in channels_found)

    def test_scan_archives_one(self):
        self.archiver.scan_archives('SR11BCM01:CURRENT_MONITOR')
        channels_found = self.archiver.archives_for_channel.keys()
        self.assertTrue('SR11BCM01:CURRENT_MONITOR' in channels_found)
        self.assertFalse('SR11BCM01:LIFETIME_MONITOR' in channels_found)
        self.assertFalse('TS01FPC01:FILL_CMD' in channels_found)

    def test_scan_archives_list(self):
        self.archiver.scan_archives(['SR11BCM01:CURRENT_MONITOR',
                                     'TS01FPC01:FILL_CMD'])
        channels_found = self.archiver.archives_for_channel.keys()
        self.assertTrue('SR11BCM01:CURRENT_MONITOR' in channels_found)
        self.assertFalse('SR11BCM01:LIFETIME_MONITOR' in channels_found)
        self.assertTrue('TS01FPC01:FILL_CMD' in channels_found)

if __name__ == '__main__':
    unittest.main()
