# -*- coding: utf-8 -*-

class ChannelNotFound(LookupError):
    '''Channel not found in archives.'''

class ChannelKeyMismatch(IndexError):
    '''There should be the same number of keys as channels'''
