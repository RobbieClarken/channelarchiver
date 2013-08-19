#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

tests_dir =  os.path.dirname(os.path.realpath(__file__))
base_dir = os.path.abspath(os.path.join(tests_dir, os.pardir))

suite = unittest.TestLoader().discover('tests', top_level_dir=base_dir)
unittest.TextTestRunner(verbosity=2).run(suite)

