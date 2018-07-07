from datetime import datetime

import pytest
from mock import Mock

from channelarchiver import Archiver, codes, utils, exceptions
from channelarchiver.models import ChannelData, ArchiveProperties
from mock_archiver import MockArchiver

utc = utils.UTC()
local_tz = utils.local_tz


@pytest.fixture
def archiver():
    archiver = Archiver("http://fake")
    archiver.archiver = MockArchiver()
    return archiver


def test_scan_archives_all(archiver):
    archiver.scan_archives()
    archives_for_channel = archiver.archives_for_channel
    assert "EXAMPLE:DOUBLE_SCALAR" in archives_for_channel
    assert "EXAMPLE:INT_WAVEFORM" in archives_for_channel
    assert "EXAMPLE:ENUM_SCALAR" in archives_for_channel
    expected_archives = {
        "EXAMPLE:DOUBLE_SCALAR": [
            ArchiveProperties(
                key=1001,
                start_time=datetime(2012, 7, 12, 21, 47, 23, 664000, tzinfo=utc),
                end_time=datetime(2012, 7, 13, 11, 18, 55, 671259, tzinfo=utc),
            )
        ],
        "EXAMPLE:INT_WAVEFORM": [
            ArchiveProperties(
                key=1001,
                start_time=datetime(2012, 7, 12, 23, 14, 19, 129600, tzinfo=utc),
                end_time=datetime(2012, 7, 13, 8, 26, 18, 558211, tzinfo=utc),
            )
        ],
        "EXAMPLE:ENUM_SCALAR": [
            ArchiveProperties(
                key=1008,
                start_time=datetime(2012, 7, 12, 22, 41, 10, 765676, tzinfo=utc),
                end_time=datetime(2012, 7, 13, 9, 20, 23, 623789, tzinfo=utc),
            )
        ],
    }
    assert archives_for_channel == expected_archives


def test_scan_archives_one(archiver):
    archiver.scan_archives("EXAMPLE:DOUBLE_SCALAR")
    archives_for_channel = archiver.archives_for_channel.keys()
    assert "EXAMPLE:DOUBLE_SCALAR" in archives_for_channel
    assert "EXAMPLE:INT_WAVEFORM" not in archives_for_channel
    assert "EXAMPLE:ENUM_SCALAR" not in archives_for_channel


def test_scan_archives_list(archiver):
    archiver.scan_archives(["EXAMPLE:DOUBLE_SCALAR", "EXAMPLE:ENUM_SCALAR"])
    archives_for_channel = archiver.archives_for_channel.keys()
    assert "EXAMPLE:DOUBLE_SCALAR" in archives_for_channel
    assert "EXAMPLE:INT_WAVEFORM" not in archives_for_channel
    assert "EXAMPLE:ENUM_SCALAR" in archives_for_channel


def test_get_scalar(archiver):
    start = datetime(2012, 1, 1, tzinfo=utc)
    end = datetime(2013, 1, 1, tzinfo=utc)
    data = archiver.get(
        ["EXAMPLE:DOUBLE_SCALAR"], start, end, interpolation=codes.interpolation.RAW
    )
    assert isinstance(data, list)
    channel_data = data[0]
    assert channel_data.channel == "EXAMPLE:DOUBLE_SCALAR"
    assert channel_data.data_type == codes.data_type.DOUBLE
    assert channel_data.elements == 1
    assert channel_data.values == [200.5, 199.9, 198.7, 196.1]
    assert channel_data.times == [
        datetime(2012, 7, 12, 21, 47, 23, 664000, utc),
        datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
        datetime(2012, 7, 13, 11, 18, 55, 671259, utc),
    ]
    assert channel_data.statuses == [0, 6, 6, 5]
    assert channel_data.severities == [0, 1, 1, 2]
    assert repr(channel_data.times[0].tzinfo) == "UTC()"


def test_get_interpolation_string(archiver):
    start = datetime(2012, 1, 1, tzinfo=utc)
    end = datetime(2013, 1, 1, tzinfo=utc)
    channel_data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR", start, end, interpolation="raw"
    )
    assert channel_data.channel == "EXAMPLE:DOUBLE_SCALAR"
    assert channel_data.values == [200.5, 199.9, 198.7, 196.1]


def test_get_scalar_str(archiver):
    start = datetime(2012, 1, 1, tzinfo=utc)
    end = datetime(2013, 1, 1, tzinfo=utc)
    channel_data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR", start, end, interpolation=codes.interpolation.RAW
    )
    assert isinstance(channel_data, ChannelData)
    assert channel_data.channel == "EXAMPLE:DOUBLE_SCALAR"
    assert channel_data.data_type == codes.data_type.DOUBLE


def test_get_scalar_in_tz(archiver):
    start = datetime(2012, 1, 1, tzinfo=utc)
    end = datetime(2013, 1, 1, tzinfo=utc)
    data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR",
        start,
        end,
        interpolation=codes.interpolation.RAW,
        tz=utils.UTC(11.5),
    )
    assert str(data.times[0].tzinfo) == "UTC+11:30"
    assert repr(data.times[0].tzinfo) == "UTC(+11.5)"


def test_get_without_scan(archiver):
    start = datetime(2012, 1, 1, tzinfo=utc)
    end = datetime(2013, 1, 1, tzinfo=utc)
    with pytest.raises(exceptions.ChannelNotFound):
        archiver.get(
            ["EXAMPLE:DOUBLE_SCALAR"],
            start,
            end,
            interpolation=codes.interpolation.RAW,
            scan_archives=False,
        )


def test_get_with_restrictive_interval(archiver):
    start = datetime(2012, 7, 13, tzinfo=utc)
    end = datetime(2012, 7, 13, 10, tzinfo=utc)
    channel_data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR", start, end, interpolation=codes.interpolation.RAW
    )
    assert channel_data.values == [199.9, 198.7]
    assert channel_data.times == [
        datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
    ]


def test_get_with_restrictive_interval_with_tzs(archiver):
    start = datetime(2012, 7, 13, 10, tzinfo=utils.UTC(10))
    end = datetime(2012, 7, 13, 20, tzinfo=utils.UTC(10))
    channel_data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR", start, end, interpolation=codes.interpolation.RAW
    )
    assert channel_data.values == [199.9, 198.7]
    assert channel_data.times == [
        datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
    ]
    assert repr(channel_data.times[0].tzinfo) == "UTC(+10)"


def test_get_with_str_times(archiver):
    start = "2012-07-13 00:00:00Z"
    end = "2012-07-13 10:00:00Z"
    channel_data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR", start, end, interpolation=codes.interpolation.RAW
    )
    assert channel_data.values == [199.9, 198.7]
    assert channel_data.times == [
        datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
    ]


def test_get_with_str_times_incl_tz(archiver):
    start = "2012-07-13 10:00:00+10:00"
    end = "2012-07-13 20:00:00+10:00"
    channel_data = archiver.get(
        "EXAMPLE:DOUBLE_SCALAR", start, end, interpolation=codes.interpolation.RAW
    )
    assert channel_data.values == [199.9, 198.7]
    assert channel_data.times == [
        datetime(2012, 7, 13, 2, 5, 1, 443589, utc),
        datetime(2012, 7, 13, 7, 19, 31, 806097, utc),
    ]
    assert repr(channel_data.times[0].tzinfo) == "UTC(+10)"


def test_get_waveform(archiver):
    start = datetime(2012, 1, 1)
    end = datetime(2013, 1, 1)
    channel_data = archiver.get(
        "EXAMPLE:INT_WAVEFORM", start, end, interpolation=codes.interpolation.RAW
    )
    assert channel_data.channel == "EXAMPLE:INT_WAVEFORM"
    assert channel_data.data_type == codes.data_type.INT
    assert channel_data.elements == 3
    assert channel_data.values == [[3, 5, 13], [2, 4, 11], [0, 7, 1]]


def test_get_enum(archiver):
    start = datetime(2012, 1, 1)
    end = datetime(2013, 1, 1)
    channel_data = archiver.get(
        "EXAMPLE:ENUM_SCALAR", start, end, interpolation=codes.interpolation.RAW
    )
    assert channel_data.channel == "EXAMPLE:ENUM_SCALAR"
    assert channel_data.data_type == codes.data_type.ENUM
    assert channel_data.values == [7, 1, 8]


def test_get_multiple(archiver):
    start = datetime(2012, 1, 1)
    end = datetime(2013, 1, 1)
    channels = ["EXAMPLE:DOUBLE_SCALAR", "EXAMPLE:INT_WAVEFORM", "EXAMPLE:ENUM_SCALAR"]
    data = archiver.get(channels, start, end, interpolation=codes.interpolation.RAW)
    assert isinstance(data, list)
    assert data[0].channel == "EXAMPLE:DOUBLE_SCALAR"
    assert data[1].channel == "EXAMPLE:INT_WAVEFORM"
    assert data[2].channel == "EXAMPLE:ENUM_SCALAR"
    assert data[0].values == [200.5, 199.9, 198.7, 196.1]
    assert data[1].values == [[3, 5, 13], [2, 4, 11], [0, 7, 1]]
    assert data[2].values == [7, 1, 8]


def test_get_with_archive_keys(archiver):
    values_mock = Mock(wraps=archiver.archiver.values)
    archiver.archiver.values = values_mock
    channels = ["EXAMPLE:GROUP1_A", "EXAMPLE:GROUP2_A", "EXAMPLE:GROUP1_B"]
    keys = [1010, 1011, 1010]
    archiver.get(
        channels,
        "2000-01-01",
        "2000-01-02",
        archive_keys=keys,
        interpolation=codes.interpolation.RAW,
    )
    first_call, second_call = values_mock.call_args_list
    assert first_call[0][:2] == (1010, ["EXAMPLE:GROUP1_A", "EXAMPLE:GROUP1_B"])
    assert second_call[0][:2] == (1011, ["EXAMPLE:GROUP2_A"])


def test_get_with_wrong_number_of_keys(archiver):
    start = datetime(2012, 1, 1)
    end = datetime(2013, 1, 1)
    with pytest.raises(exceptions.ChannelKeyMismatch):
        archiver.get(
            ["EXAMPLE:DOUBLE_SCALAR"],
            start,
            end,
            archive_keys=[1001, 1008],
            interpolation=codes.interpolation.RAW,
        )
