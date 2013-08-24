# -*- coding: utf-8 -*-

'''
channelarchiver is a library for retrieving data from an EPICS Channel
Archiver. It does the hard work of figuring out which archives contain
the appropriate data for times and channels you specify.

Example usage:

    >>> from channelarchiver import Archiver
    >>> archiver = Archiver('http://cr01arc01/cgi-bin/ArchiveDataServer.cgi')
    >>> channels = ['SR11BCM01:LIFETIME_MONITOR', 'SR11BCM01:CURRENT_MONITOR']
    >>> start = '2013-08-10 09:00+10:00'
    >>> end = '2013-08-15 23:00+10:00'
    >>> lifetime, current = archiver.get(channels, start, end)
    >>> lifetime.values
    [25.8, 25.7, ..., 26.1]
'''


__title__ = 'channelarchiver'
__version_info__ = (0, 0, 2)
__version__ = '.'.join(map(str, __version_info__))
__license__ = 'MIT'

from .channelarchiver import Archiver
from . import codes
