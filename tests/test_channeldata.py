import datetime

import pytest

from channelarchiver import codes, utils
from channelarchiver.models import ChannelData, Limits


utc = utils.UTC()


@pytest.fixture
def scalar_channel():
    values = [200.5, 199.9, 198.7, 196.1]
    times = [
        datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
        datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
        datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc),
    ]
    return ChannelData(
        channel="EXAMPLE:DOUBLE_SCALAR",
        values=values,
        times=times,
        statuses=[0, 6, 6, 5],
        severities=[0, 1, 1, 2],
        units="mA",
        states=None,
        data_type=codes.data_type.DOUBLE,
        elements=1,
        display_limits=Limits(0, 220),
        warn_limits=Limits(199, 210),
        alarm_limits=Limits(198, 220),
        display_precision=3,
        archive_key=1001,
    )


@pytest.fixture
def array_channel():
    array_values = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        [
            100,
            99,
            98,
            97,
            96,
            95,
            94,
            93,
            92,
            91,
            90,
            89,
            88,
            87,
            86,
            85,
            84,
            83,
            82,
            81,
        ],
    ]
    tz = utils.UTC(10)
    array_times = [
        datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, tz),
        datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, tz),
    ]
    return ChannelData(
        channel="EXAMPLE:DOUBLE_SCALAR",
        values=array_values,
        times=array_times,
        statuses=[0, 6],
        severities=[0, 1],
        units="mA",
        states=None,
        data_type=codes.data_type.DOUBLE,
        elements=20,
        display_limits=Limits(0, 220),
        warn_limits=Limits(199, 210),
        alarm_limits=Limits(198, 220),
        display_precision=3,
        archive_key=1001,
    )


def test_get_properties(scalar_channel):
    assert scalar_channel.channel == "EXAMPLE:DOUBLE_SCALAR"
    assert scalar_channel.values == [200.5, 199.9, 198.7, 196.1]
    assert scalar_channel.times == [
        datetime.datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
        datetime.datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime.datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
        datetime.datetime(2012, 7, 13, 11, 18, 55, 671259, utc),
    ]
    assert scalar_channel.statuses == [0, 6, 6, 5]
    assert scalar_channel.severities == [0, 1, 1, 2]
    assert scalar_channel.units == "mA"
    assert scalar_channel.states is None
    assert scalar_channel.data_type == codes.data_type.DOUBLE
    assert scalar_channel.elements == 1
    assert scalar_channel.display_limits == Limits(0, 220)
    assert scalar_channel.warn_limits == Limits(199, 210)
    assert scalar_channel.alarm_limits == Limits(198, 220)
    assert scalar_channel.display_precision == 3
    assert scalar_channel.archive_key == 1001


def test_scalar_str(scalar_channel):
    expected_str = (
        "               time  value      status  severity\n"
        "2012-07-12 21:47:23  200.5    NO_ALARM  NO_ALARM\n"
        "2012-07-13 02:05:01  199.9   LOW_ALARM     MINOR\n"
        "2012-07-13 07:19:31  198.7   LOW_ALARM     MINOR\n"
        "2012-07-13 11:18:55  196.1  LOLO_ALARM     MAJOR"
    )
    assert str(scalar_channel) == expected_str


def test_array_str(array_channel):
    expected_str = (
        "               time                                value     status  severity\n"  # noqa
        "2012-07-12 21:47:23  [  0,   1,   2,   3,   4,   5,   6,   NO_ALARM  NO_ALARM\n"  # noqa
        "                        7,   8,   9,  10,  11,  12,  13,                     \n"  # noqa
        "                       14,  15,  16,  17,  18,  19]                          \n"  # noqa
        "2012-07-13 02:05:01  [100,  99,  98,  97,  96,  95,  94,  LOW_ALARM     MINOR\n"  # noqa
        "                       93,  92,  91,  90,  89,  88,  87,                     \n"  # noqa
        "                       86,  85,  84,  83,  82,  81]"
    )
    assert str(array_channel) == expected_str
