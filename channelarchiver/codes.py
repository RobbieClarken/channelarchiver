# -*- coding: utf-8 -*-

from .structures import Codes

status = Codes(
    NO_ALARM = 0,
    READ_ALARM = 1,
    WRITE_ALARM = 2,
    HIHI_ALARM = 3,
    HIGH_ALARM = 4,
    LOLO_ALARM = 5,
    LOW_ALARM = 6,
    STATE_ALARM = 7,
    COS_ALARM = 8,
    COMM_ALARM = 9,
    TIMEOUT_ALARM = 10,
    HWLIMIT_ALARM = 11,
    CALC_ALARM = 12,
    SCAN_ALARM = 13,
    LINK_ALARM = 14,
    SOFT_ALARM = 15,
    BAD_SUB_ALARM = 16,
    UDF_ALARM = 17,
    DISABLE_ALARM = 18,
    SIMM_ALARM = 19,
    READ_ACCESS_ALARM = 20,
    WRITE_ACCESS_ALARM = 21
)

severity = Codes(
    NO_ALARM = 0,
    MINOR = 1,
    MAJOR = 2,
    INVALID = 3,
    EST_REPEAT = 3968,
    REPEAT = 3856,
    DISCONNECTED = 3904,
    ARCHIVE_OFF = 3872,
    ARCHIVE_DISABLED = 3848,
)

interpolation = Codes(
    RAW = 0,
    SPREADSHEET = 1,
    AVERAGED = 2,
    PLOT_BINNING = 3,
    LINEAR = 4,
)

data_type = Codes(
    STRING = 0,
    ENUM = 1,
    INT = 2,
    DOUBLE = 3,
)

xmlrpc = Codes(
    UNSPECIFIED = 0,
    INTERNAL = -500,
    TYPE = -501,
    INDEX = -502,
    PARSE = -503,
    NETWORK = -504,
    TIMEOUT = -505,
    NO_SUCH_METHOD = -506,
    REQUEST_REFUSED = -507,
    INTROSPECTION_DISABLED = -508,
    LIMIT_EXCEEDED = -509,
    INVALID_UTF8 = -510,
)

archiver = Codes(
    SEVER_FAULT = -600,
    NO_INDEX = -601,
    ARGUMENT_ERROR = -602,
    DATA_ERROR = -603,
)
