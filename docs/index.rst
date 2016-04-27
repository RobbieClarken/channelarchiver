.. channelarchiver documentation master file, created by
   sphinx-quickstart on Wed Apr 27 10:48:10 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

channelarchiver
===============

A python client for retrieving data from an EPICS Channel Archiver.

To get started just import the ``Archiver`` class and specify the
address of your Channel Archiver server::

    >>> from channelarchiver import Archiver
    >>> url = 'http://cr01arc01/cgi-bin/ArchiveDataServer.cgi'
    >>> archiver = Archiver(url)

You then fetch data with the ``archiver.get()`` method::

    >>> data = archiver.get('CHAN:MON', '2013-08-11', '2013-08-12')
    >>> print(data)
                   time        value     status      severity
    2013-08-11 00:00:02   96.9351518   NO_ALARM      NO_ALARM
    2013-08-11 00:04:20   94.5171233   NO_ALARM      NO_ALARM
    2013-08-11 00:08:38   85.0604361  LOW_ALARM         MINOR
    ...
    >>> data.values
    [96.935, 94.517, ..., 97.253]


User Guide
----------

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

