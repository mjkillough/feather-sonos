#!/usr/bin/env python
# encoding: utf-8

import errno
import socket
import time

import upnp


def discover_ips(timeout=2):
    """Discover Sonos devices on local network and generate their IPs.

    Accepts optional `timeout` parameter, which gives total timeout in seconds.
    """
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
            if e.args[0] != errno.ETIMEDOUT:
                raise
        else:
            if b'Sonos' in data and ip not in discovered:
                discovered.add(ip)
                yield ip
            time.sleep(0.1)
