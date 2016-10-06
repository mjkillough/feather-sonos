#!/usr/bin/env python
# encoding: utf-8

"""Run test_*.py files that are baked into MicroPython image."""

import os
import unittest


if __name__ == '__main__':
    # Sad to have to define these here as well as in the Makefile, but ampy
    # doesn't seem to be able to pass arguments to scripts. We can't do
    # os.listdir(), as the modules are baked into the firmware image.
    for module_name in ['test_sonos', 'test_discovery', 'test_upnp']:
        unittest.main(module_name)
