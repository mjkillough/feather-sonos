#!/usr/bin/env python
# encoding: utf-8


class mock:
    """Poor man's unittest.mock.

    The MicroPython standard library doesn't seem to have unittest.mock.
    """

    def __init__(self, owner, method_name, return_value):
        self.owner = owner
        self.method_name = method_name
        self.return_value = return_value

    def __enter__(self):
        def mocked(*args, **kwargs):
            return self.return_value
        self.original = getattr(self.owner, self.method_name)
        setattr(self.owner, self.method_name, mocked)

    def __exit__(self, *unused):
        setattr(self.owner, self.method_name, self.original)
