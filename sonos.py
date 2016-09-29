#!/usr/bin/env python
# encoding: utf-8

import errno
import socket
import time

try:
    import uio as io
except ImportError:
    import io

import xmltok

import upnp


BASE_URL_TEMPLATE = 'http://%s:1400'


class Sonos(object):
    """Represents a Sonos device (usually a speaker).

    Usually you'd access the Sonos instance for the controller of a group. The
    other devices in the group are stored on `Sonos.other_players`.

    This class isn't really meant to manage group membership (as `soco.SoCo`
    instances do), and so it assumes group membership doesn't change after it's
    created.
    """

    def __init__(self, uuid, ip, name):
        self.uuid = uuid
        self.ip = ip
        self.name = name
        self.other_players = []
        self._base_url = BASE_URL_TEMPLATE % self.ip

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        # We really only need to check the UUIDs match, but we'll test all
        # of our important fields match, so that we can use this for asserts
        # in the tests.
        return (
            self.uuid == other.uuid and
            self.ip == other.ip and
            self.name == other.name
        )

    def __repr__(self):
        return '<Sonos uuid=%s, ip=%s, name=%s, other_players=%r>' % (
            self.uuid, self.ip, self.name, self.other_players
        )

    def add_player_to_group(self, player):
        self.other_players.append(player)

    def _issue_av_transport_command(self, command):
        # Play/Pause/Next are all very similar.
        return upnp.send_command(
            self._base_url + '/MediaRenderer/AVTransport/Control',
            'AVTransport', 1, command, [('InstanceID', 0), ('Speed', 1)]
        )

    def play(self):
        self._issue_av_transport_command('Play')
    def pause(self):
        self._issue_av_transport_command('Pause')
    def next(self):
        self._issue_av_transport_command('Next')

    def add_player_to_group(self, player):
        self.other_players.append(player)
