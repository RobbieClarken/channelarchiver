A python client for retrieving data from an EPICS Channel Archiver.

To get started just import the `Archiver` class and specify the address of your Channel Archiver server:

```python
from channelarchiver import Archiver
archiver = Archiver('http://cr01arc01/cgi-bin/ArchiveDataServer.cgi')
```

You then fetch data with the `archiver.get()` method:

```python
>>> data = archiver.get('SR00IE01:INJECTION_EFFICIENCY_MONITOR', '2013-08-11', '2013-08-12')
>>> print data
               time        value     status      severity
2013-08-11 00:00:02   96.9351518   NO_ALARM      NO_ALARM
2013-08-11 00:04:20   94.5171233   NO_ALARM      NO_ALARM
2013-08-11 00:08:38   85.0604361  LOW_ALARM         MINOR
...
>>> data.values
[96.935, 94.517, ..., 97.253]
```

The returned `ChannelData` object has the following fields:

* `times`: A list of datetimes.
* `values`: A list of the channel's values corresponding to `times`.
* `severities` and `statuses`: Diagnostic information about the channel state for each time.
* `units`
* `states`: String values for enum type channels.
* `data_type`: Whether the channel values are string, enum, int or double (see `codes.data_type`).
* `elements`: The number of elements in an array type channel.
* `display_limits`, `warn_limits`, `alarm_limits`: Low and high limits
* `display_precision`: The recommended number of decimal places to to display values with in user interfaces.

