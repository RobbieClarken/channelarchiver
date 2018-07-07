#!/usr/bin/env python

from setuptools import setup
import re

with open("channelarchiver/__init__.py") as file:
    version = re.search(r'__version__ = "(.*)"', file.read()).group(1)

setup(
    name="channelarchiver",
    version=version,
    description="Python client for the EPICS Channel Archiver.",
    long_description=open("README.rst").read(),
    license=open("LICENSE.rst").read(),
    author="Robbie Clarken",
    author_email="robbie.clarken@gmail.com",
    url="https://github.com/RobbieClarken/channelarchiver",
    packages=["channelarchiver"],
    install_requires=["tzlocal"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved :: MIT License",
    ],
)
