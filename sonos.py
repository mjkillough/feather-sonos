#!/usr/bin/env python
# encoding: utf-8

import errno
import socket
import time

import upnp


DEFAULT_DISCOVER_TIMEOUT = 2


def _discover_ips(timeout=DEFAULT_DISCOVER_TIMEOUT):
    """Discover Sonos devices on local network and generate their IPs."""
    MCAST_GRP = '239.255.255.250'
    MCAST_PORT = 1900
    PLAYER_SEARCH = '\n'.join((
        'M-SEARCH * HTTP/1.1',
        'HOST: 239.255.255.250:1900',
        'MAN: "ssdp:discover"',
        'MX: 1',
        'ST: urn:schemas-upnp-org:device:ZonePlayer:1',
    )).encode('utf-8')

    # We have to set non-blocking mode and poll the socket, as MicroPython
    # doesn't give us anything better on the ESP8266
    # TODO: #7 - see if provisional select.poll() PR works well enough.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    # Send a few times, just in case UDP gives us trouble.
    for _ in range(3):
        sock.sendto(PLAYER_SEARCH, (MCAST_GRP, MCAST_PORT))

    start_time = time.time()
    end_time = start_time + timeout
    discovered = set()
    while True:
        if time.time() >= end_time:
            break
        try:
            data, (ip, port) = sock.recvfrom(1024)
        except OSError as e:
            # MicroPython returns ETIMEDOUT, but CPython 3.5 returns EAGAIN.
            if e.args[0] not in (errno.ETIMEDOUT, errno.EAGAIN):
                raise
        else:
            if b'Sonos' in data and ip not in discovered:
                discovered.add(ip)
                yield ip
            time.sleep(0.1)


def discover(timeout=DEFAULT_DISCOVER_TIMEOUT):
    """Discover Sonos devices on local network and returns as `Sonos` instances.

    Accepts optional `timeout` parameter, which gives total timeout in seconds.
    """
    for ip in _discover_ips(timeout):
        yield Sonos(ip)


class Sonos(object):
    """Represents a Sonos device (usually a speaker)"""

    def __init__(self, ip):
        self.ip = ip

    @property
    def _base_url(self):
        return 'http://%s:1400' % self.ip

    @property
    def _av_transport_url(self):
        return self._base_url + '/MediaRenderer/AVTransport/Control'

    def _issue_av_transport_command(self, command):
        # Play/Pause/Next are all very similar.
        return upnp.send_command(
            self._av_transport_url,
            'AVTransport', 1, command, [('InstanceID', 0), ('Speed', 1)]
        )

    def play(self):
        self._issue_av_transport_command('Play')
    def pause(self):
        self._issue_av_transport_command('Pause')
    def next(self):
        self._issue_av_transport_command('Next')
