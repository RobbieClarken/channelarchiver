# -*- coding: utf-8 -*-

class status(object):
    NO_ALARM = 0
    READ = 1
    WRITE = 2
    HIHI = 3
    HIGH = 4
    LOLO = 5
    LOW = 6
    STATE = 7
    COS = 8
    COMM = 9
    TIMEOUT = 10
    HWLIMIT = 11
    CALC = 12
    SCAN = 13
    LINK = 14
    SOFT = 15
    BAD_SUB = 16
    UDF = 17
    DISABLE = 18
    SIMM = 19
    READ_ACCESS = 20
    WRITE_ACCESS = 21

class severity(object):
    NO_ALARM = 0
    MINOR = 1
    MAJOR = 2
    INVALID = 3
    EST_REPEAT = 3968
    REPEAT = 3856
    DISCONNECTED = 3904
    ARCHIVE_OFF = 3872
    ARCHIVE_DISABLED = 3848

class interpolate(object):
    RAW = 0
    SPREADSHEET = 1
    AVERAGED = 2
    PLOT_BINNING = 3
    LINEAR = 4

class data_type(object):
    STRING = 0
    ENUM = 1
    INT = 2
    DOUBLE = 3

class xmlrpc(object):
    UNSPECIFIED = 0
    INTERNAL = -500
    TYPE = -501
    INDEX = -502
    PARSE = -503
    NETWORK = -504
    TIMEOUT = -505
    NO_SUCH_METHOD = -506
    REQUEST_REFUSED = -507
    INTROSPECTION_DISABLED = -508
    LIMIT_EXCEEDED = -509
    INVALID_UTF8 = -510

class archiver(object):
    SEVER_FAULT = -600
    NO_INDEX = -601
    ARGUMENT_ERROR = -602
    DATA_ERROR = -603
