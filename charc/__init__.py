# -*- coding: utf-8 -*-

'''
charc is a library for retrieving data from an EPICS Channel Archiver. It does the hard work of figuring out which archives contain the appropriate data for times and channels you specify.

Example usage:

    >>> import charc
    >>> archiver = charc.Archiver('http://cr01arc01/cgi-bin/ArchiveDataServer.cgi')
    >>> channel_names = ['SR11BCM01:LIFETIME_MONITOR', 'SR00IE01:INJECTION_EFFICIENCY_MONITOR']
    >>> start = datetime.datetime(2013, 7, 20)
    >>> end = datetime.datetime(2013, 7, 21)
    >>> lifetime, efficiency = archiver.get(channel_names, start, end)
'''


__title__ = 'charc'
__version_info__ = (0, 0, 0)
__version__ = '.'.join(map(str, __version_info__))
__license__ = 'MIT'

from .charc import Archiver
import codes
