# -*- coding: utf-8 -*-

from collections import namedtuple

ArchiveProperties = namedtuple('ArchiveProperties',
                               'key start_time end_time')

Limits = namedtuple('Limits', 'low high')
