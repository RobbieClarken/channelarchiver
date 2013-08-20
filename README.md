A python client for retrieving data from an EPICS Channel Archiver.

To get started just import the `Archiver` class and specify the address of your Channel Archiver server:

```python
from channelarchiver import Archiver
archiver = Archiver('http://cr01arc01/cgi-bin/ArchiveDataServer.cgi')
```

You then fetch data with the `archiver.get()` method:

```python
>>> start = datetime.datetime(2013, 8, 11)
>>> end = datetime.datetime(2013, 8, 12)
>>> data = archiver.get('SR00IE01:INJECTION_EFFICIENCY_MONITOR', start, end)
>>> data.values
[96.935, 94.517, ..., 97.253]
```
