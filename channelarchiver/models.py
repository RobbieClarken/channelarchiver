# -*- coding: utf-8 -*-

from collections import namedtuple

from . import codes
from . import utils
from . import exceptions


try:
    import numpy as np
except ImportError:
    HAS_NUMPY = False
else:
    HAS_NUMPY = True


ArchiveProperties = namedtuple("ArchiveProperties", "key start_time end_time")
Limits = namedtuple("Limits", "low high")


class ChannelData(object):
    """
    Container for archive data for a single channel.

    Attributes:
        channel (str): The channel name.
        values (List): A list of channel values.
        times (List[datetime]): Timestamps corresponding to the retrieved values.
        statuses (List[int]): Status values corresponding with the retrieved values.
        severities (List[int]): Severity values corresponding with the retrieved
            values.
        units (str): The units of the values.
        states (List[str]): The states a STRING or ENUM can have.
        data_type (int): The data type of the channel.
        elements (int): The number of elements per sample for waveform channels.
        display_limits (Limits): Values advising how to display the values in a user
            interface.
        warn_limits (Limits): Low and high values for which the channel will
            generate a warning.
        alarm_limits (Limits): Low and high values for which the channel will
            generate an alarm.
        display_precision (int): The number of decimal places to show in user
            interfaces.
        archive_key (int): The archive the data was pulled from.

    """

    def __init__(
        self,
        channel=None,
        values=None,
        times=None,
        statuses=None,
        severities=None,
        units=None,
        states=None,
        data_type=None,
        elements=None,
        display_limits=None,
        warn_limits=None,
        alarm_limits=None,
        display_precision=None,
        archive_key=None,
        interpolation=None,
    ):

        super(ChannelData, self).__init__()

        self.channel = channel
        self.values = values
        self.times = times
        self.statuses = statuses
        self.severities = severities
        self.units = units
        self.states = states
        self.data_type = data_type
        self.elements = elements
        self.display_limits = display_limits
        self.warn_limits = warn_limits
        self.alarm_limits = alarm_limits
        self.display_precision = display_precision
        self.archive_key = archive_key
        self.interpolation = interpolation
        self._array = None

    @property
    def array(self):
        """Return the data in a numpy array structure."""

        if not HAS_NUMPY:
            raise exceptions.NumpyNotInstalled("Numpy not found")

        # Only compute the array once
        if self._array is None:

            if self.data_type == codes.data_type.STRING:
                value_dtype = np.str
            elif self.data_type == codes.data_type.ENUM:
                value_dtype = np.uint8
            elif self.data_type == codes.data_type.INT:
                value_dtype = np.int
            else:
                value_dtype = np.dtype(float)

            dtypes = [
                ("time", np.dtype("datetime64[us]")),
                ("value", value_dtype, self.elements),
                ("status", np.uint8),
                ("severity", np.uint16),
            ]

            data = zip(self.times, self.values, self.statuses, self.severities)

            self._array = np.array(data, dtype=dtypes)

        return self._array

    def __repr__(self):

        if self.data_type == codes.data_type.DOUBLE:
            fmt = "{0:.6g}"
        else:
            fmt = "{0!r}"

        s = "ChannelData(\n"
        if self.elements == 1:
            s += utils.pretty_list_repr(self.values, fmt, prefix="    values=")
        else:
            s += utils.pretty_waveform_repr(self.values, fmt, prefix="    values=")
        s += ",\n"
        for attr in ["times", "statuses", "severities", "states"]:
            value = self.__getattribute__(attr)
            if value is None:
                continue
            prefix = f"    {attr}="
            s += utils.pretty_list_repr(value, prefix=prefix)
            s += ",\n"
        for attr in [
            "units",
            "data_type",
            "elements",
            "display_limits",
            "warn_limits",
            "alarm_limits",
            "display_precision",
            "archive_key",
            "interpolation",
        ]:
            value = self.__getattribute__(attr)
            if value is None:
                continue
            s += f"    {attr}={value!r},\n"
        s = s[:-2]
        s += "\n)"
        return s

    def __str__(self):
        times = ["time"] + [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in self.times]
        statuses = ["status"] + [codes.status.str_value(s) for s in self.statuses]
        severities = ["severity"] + [
            codes.severity.str_value(s) for s in self.severities
        ]
        times_len = max(len(s) for s in times)
        statuses_len = max(len(s) for s in statuses)
        severities_len = max(len(s) for s in severities)
        out = ""
        value_format = "{0:.9g}"
        if self.elements == 1:
            values = ["value"] + [value_format.format(v) for v in self.values]
        else:
            len_for_values = 79 - times_len - statuses_len - severities_len - 6
            values = ["value"]
            max_value_len = utils.max_value_len_in_waveform(self.values, value_format)
            for value in self.values:
                formatted_value = utils.pretty_list_repr(
                    value,
                    value_format,
                    max_line_len=len_for_values,
                    min_value_len=max_value_len,
                )
                values += formatted_value.split("\n")

        values_len = max(len(s) for s in values)
        spec = (
            "{0:>" + str(times_len) + "}  "
            "{1:>" + str(values_len) + "}  "
            "{2:>" + str(statuses_len) + "}  "
            "{3:>" + str(severities_len) + "}\n"
        )

        if self.elements == 1:
            for fields in zip(times, values, statuses, severities):
                out += spec.format(*fields)
        else:
            i = 0
            for line in values:
                if i == 0 or "[" in line:
                    out += spec.format(times[i], line, statuses[i], severities[i])
                    i += 1
                else:
                    out += spec.format("", line.ljust(values_len), "", "")
        return out.rstrip()
