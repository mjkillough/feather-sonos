#!/usr/bin/env python
# encoding: utf-8

import types
import unittest

import discovery
import sonos
import upnp
import testhelpers


DIDL_XML = (
    '<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        ' xmlns:r="urn:schemas-rinconnetworks-com:metadata-1-0/"'
        ' xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/">'
        '<item id="-1" parentID="-1">'
            '<res duration="0:04:21" protocolInfo="http-get:*:audio/x-spotify:*">x-sonos-spotify:spotify%3atrack%3a43kwXa3KgzSOsYzimWbHXn?sid=9&amp;flags=0&amp;sn=1</res>'
            '<upnp:albumArtURI>https://i.scdn.co/image/636e9bce43e949a04b6dbe29ce5227ae180fbea6</upnp:albumArtURI>'
            '<upnp:class>object.item.audioItem.musicTrack</upnp:class>'
            '<dc:title>Knees to the Floor</dc:title>'
            '<dc:creator>Francis and the Lights</dc:creator>'
            '<r:albumArtist>Francis and the Lights</r:albumArtist>'
            '<upnp:album>It\'ll Be Better</upnp:album>'
            '<r:tiid>-2022898489</r:tiid>'
        '</item>'
    '</DIDL-Lite>'
)
GET_POSITION_INFO_RESPONSE = {
    'AbsCount': '2147483647',
    'AbsTime': 'NOT_IMPLEMENTED',
    'RelCount': '2147483647',
    'RelTime': '0:00:42',
    'Track': '3',
    'TrackDuration': '0:04:21',
    'TrackMetaData': DIDL_XML,
    'TrackURI': 'x-sonos-spotify:spotify%3atrack%3a43kwXa3KgzSOsYzimWbHXn?sid=9&flags=0&sn=1'
}


class SonosTests(unittest.TestCase):

    def test_get_current_track_info(self):
        s = sonos.Sonos('', '', '')
        with testhelpers.mock(s, '_issue_av_transport_command', GET_POSITION_INFO_RESPONSE):
            track_info = s.get_current_track_info()
            self.assertIsInstance(track_info, sonos.TrackInfo)
            self.assertEqual(track_info.total_time, '0:04:21')
            self.assertEqual(track_info.current_time, '0:00:42')
            self.assertEqual(track_info.artist, 'Francis and the Lights')
            self.assertEqual(track_info.album, 'It\'ll Be Better')
            self.assertEqual(track_info.title, 'Knees to the Floor')

    def test_no_current_track(self):
        s = sonos.Sonos('', '', '')
        with testhelpers.mock(s, '_issue_av_transport_command', dict()):
            track_info = s.get_current_track_info()
            self.assertIs(track_info, None)


if __name__ == '__main__':
    unittest.main()
