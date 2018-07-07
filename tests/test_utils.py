from datetime import datetime, timedelta, tzinfo

import pytest
import pytz

from channelarchiver import utils


class AEST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=10)

    def dst(self, dt):
        return timedelta(0)


melbourne_tz = pytz.timezone("Australia/Melbourne")


def test_utc():
    tz = utils.UTC()
    assert tz.tzname() == "UTC"
    assert repr(tz) == "UTC()"


def test_utc_with_offset():
    hours = 6 + 3. / 60.
    tz = utils.UTC(hours)
    assert tz.tzname() == "UTC+06:03"
    assert repr(tz) == "UTC(+6.05)"


def test_utc_with_negative_offset():
    hours = -(6 + 45. / 60.)
    tz = utils.UTC(hours)
    assert tz.tzname() == "UTC-06:45"
    assert repr(tz) == "UTC(-6.75)"


def test_utc_with_offset_seconds():
    hours = 23 + 15. / 60. + 8. / 3600.
    tz = utils.UTC(hours)
    assert tz.tzname() == "UTC+23:15:08"
    assert repr(tz) == "UTC(+23.252222)"


def test_datetime_isoformat():
    iso_str = "2013-08-07 10:21:55.012345"
    dt = utils.datetime_from_isoformat(iso_str)
    dt_correct = utils.local_tz.localize(datetime(2013, 8, 7, 10, 21, 55, 12345))
    assert dt == dt_correct


def test_datetime_isoformat_with_dst():
    iso_str = "2013-02-07 10:21:55.012345"
    local_tz = utils.local_tz
    utils.local_tz = melbourne_tz
    dt = utils.datetime_from_isoformat(iso_str)
    utils.local_tz = local_tz
    assert dt.utcoffset() == timedelta(0, 39600)
    dt_correct = melbourne_tz.localize(datetime(2013, 2, 7, 10, 21, 55, 12345))
    assert dt == dt_correct


def test_datetime_isoformat_with_T():
    iso_str = "2013-08-07T10:21:55.012345"
    dt = utils.datetime_from_isoformat(iso_str)
    dt_correct = utils.local_tz.localize(datetime(2013, 8, 7, 10, 21, 55, 12345))
    assert dt == dt_correct


def test_datetime_isoformat_with_Z():
    iso_str = "2013-08-07 10:21:55.012345Z"
    dt = utils.datetime_from_isoformat(iso_str)
    assert dt == datetime(2013, 8, 7, 10, 21, 55, 12345, utils.utc)


def test_datetime_isoformat_with_tz():
    iso_str = "2013-08-07 10:21:55.012345+10:00"
    dt = utils.datetime_from_isoformat(iso_str)
    assert dt == datetime(2013, 8, 7, 10, 21, 55, 12345, utils.UTC(10))


def test_datetime_isoformat_with_short_tz():
    iso_str = "2013-08-07 10:21:55.012345+08"
    dt = utils.datetime_from_isoformat(iso_str)
    assert dt == datetime(2013, 8, 7, 10, 21, 55, 12345, utils.UTC(8))


def test_datetime_isoformat_no_ms():
    iso_str = "2013-08-07 10:21:55Z"
    dt = utils.datetime_from_isoformat(iso_str)
    assert dt == datetime(2013, 8, 7, 10, 21, 55, 0, utils.utc)


def test_datetime_isoformat_no_secs():
    iso_str = "2013-08-07 10:21Z"
    dt = utils.datetime_from_isoformat(iso_str)
    assert dt == datetime(2013, 8, 7, 10, 21, 0, 0, utils.utc)


def test_datetime_isoformat_no_secs_tz():
    iso_str = "2013-08-07 10:21-09:00"
    dt = utils.datetime_from_isoformat(iso_str)
    assert dt == datetime(2013, 8, 7, 10, 21, 0, 0, utils.UTC(-9))


def test_datetime_isoformat_no_hrs():
    iso_str = "2013-08-07"
    dt = utils.datetime_from_isoformat(iso_str)
    dt_correct = utils.local_tz.localize(datetime(2013, 8, 7, 0, 0, 0, 0))
    assert dt == dt_correct


def test_datetime_isoformat_bad_str():
    iso_str = "09:00 21/08/2103"
    with pytest.raises(ValueError):
        utils.datetime_from_isoformat(iso_str)


def test_datetime_from_sec_and_nano():
    seconds = 1376706013
    nanoseconds = 123456789
    dt = utils.datetime_from_sec_and_nano(seconds, nanoseconds)
    # Note nanoseconds get rounded off in conversion to microseconds
    assert dt == datetime(2013, 8, 17, 2, 20, 13, 123457, utils.utc)


def test_datetime_from_sec_and_nano_near_1e9_ns():
    seconds = 1376706013
    nanoseconds = 999999500
    dt = utils.datetime_from_sec_and_nano(seconds, nanoseconds)
    # Note nanoseconds get rounded off in conversion to microseconds
    assert dt == datetime(2013, 8, 17, 2, 20, 14, 0, utils.utc)


def test_datetime_from_sec_and_nano_with_utc():
    seconds = 1342129643
    nanoseconds = 123456789
    dt = utils.datetime_from_sec_and_nano(seconds, nanoseconds, utils.utc)
    # Note nanoseconds get rounded off in conversion to microseconds
    assert dt == datetime(2012, 7, 12, 21, 47, 23, 123457, utils.utc)


def test_datetime_from_sec_and_nano_with_tz():
    seconds = 1376706013
    nanoseconds = 123456789
    tz = AEST()
    dt = utils.datetime_from_sec_and_nano(seconds, nanoseconds, tz)
    assert dt == datetime(2013, 8, 17, 12, 20, 13, 123457, AEST())


def test_datetime_from_sec_and_nano_with_dst():
    seconds = 1392663073
    nanoseconds = 987654321
    dt = utils.datetime_from_sec_and_nano(seconds, nanoseconds, melbourne_tz)
    dt_correct = melbourne_tz.localize(datetime(2014, 2, 18, 5, 51, 13, 987654))
    assert dt == dt_correct
    assert dt.utcoffset() == timedelta(0, 39600)


def test_sec_and_nano_from_datetime():
    dt = datetime(2013, 8, 17, 2, 20, 13, 123456)
    seconds, nanoseconds = utils.sec_and_nano_from_datetime(dt)
    assert seconds == 1376706013
    assert nanoseconds == 123456000


def test_sec_and_nano_from_datetime_with_tz():
    dt = datetime(2013, 8, 17, 12, 20, 13, 123456, AEST())
    seconds, nanoseconds = utils.sec_and_nano_from_datetime(dt)
    assert seconds == 1376706013
    assert nanoseconds == 123456000


def test_overlap_between_intervals():
    first_range_start = datetime(2013, 8, 17, 2, 20, 13, 123456, utils.utc)
    second_range_start = first_range_start + timedelta(hours=1)
    second_range_end = first_range_start + timedelta(hours=2)
    first_range_end = first_range_start + timedelta(hours=3)
    second_range_start = second_range_start.astimezone(AEST())
    second_range_end = second_range_end.astimezone(AEST())
    overlap = utils.overlap_between_intervals(
        first_range_start, first_range_end, second_range_start, second_range_end
    )
    assert overlap == timedelta(hours=1)


def test_overlap_between_intervals_no_union():
    first_range_start = datetime(2013, 8, 17, 2, 20, 13, 123456, utils.utc)
    first_range_end = first_range_start + timedelta(hours=1)
    second_range_start = first_range_start + timedelta(hours=2)
    second_range_end = first_range_start + timedelta(hours=3)

    overlap = utils.overlap_between_intervals(
        first_range_start, first_range_end, second_range_start, second_range_end
    )
    assert overlap == timedelta(0)


def test_overlap_between_intervals_no_subset():
    first_range_start = datetime(2013, 8, 17, 2, 20, 13, 123456, utils.utc)
    second_range_start = first_range_start + timedelta(hours=1)
    first_range_end = first_range_start + timedelta(hours=2)
    second_range_end = first_range_start + timedelta(hours=3)

    overlap = utils.overlap_between_intervals(
        first_range_start, first_range_end, second_range_start, second_range_end
    )
    assert overlap == timedelta(hours=1)


def test_pretty_list_repr():
    lst = [8, 3, 3, 14, 4, 4, 6, 5, 14, 9, 13, 2, 18, 10, 4, 15, 12]
    assert utils.pretty_list_repr(lst, max_line_len=40) == (
        "[ 8,  3,  3, 14,  4,  4,  6,  5, 14,  9,\n" " 13,  2, 18, 10,  4, 15, 12]"
    )


def test_pretty_list_repr_no_wrap():
    lst = [8, 3, 3, 14, 4, 4, 6, 5, 14, 9, 13, 2, 18, 10, 4, 15, 12]
    assert utils.pretty_list_repr(lst, max_line_len=80) == (
        "[ 8,  3,  3, 14,  4,  4,  6,  5, 14,  9," " 13,  2, 18, 10,  4, 15, 12]"
    )


def test_pretty_list_format():
    lst = [123.92704029, 1.98628919, 20.99657472, 6.69566871, 5.0193061]
    lst_repr = utils.pretty_list_repr(lst, max_line_len=20, value_format="{0:.3f}")
    expected_repr = "[123.927,   1.986,\n  20.997,   6.696,\n   5.019]"
    assert lst_repr == expected_repr


def test_pretty_list_repr_str_list():
    lst = ["Apple", "Banana", "Tina's Pear", "Red", "Green", "Blue"]
    lst_repr = utils.pretty_list_repr(lst, max_line_len=30)
    assert lst_repr == (
        """[      'Apple',      'Banana',\n"""
        """ "Tina's Pear",         'Red',\n"""
        """       'Green',        'Blue']"""
    )


def test_pretty_list_repr_empty_list():
    lst = []
    lst_repr = utils.pretty_list_repr(lst)
    assert lst_repr == "[]"


def test_pretty_waveform_repr():
    lst = [[1, 5, 7], [20, 2, 9]]
    lst_repr = utils.pretty_waveform_repr(lst, max_line_len=15)
    assert lst_repr == "[[ 1,  5,  7],\n [20,  2,  9]]"


def test_pretty_waveform_repr_empty_list():
    lst = []
    lst_repr = utils.pretty_list_repr(lst)
    assert lst_repr == "[]"
