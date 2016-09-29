#!/usr/bin/env python
# encoding: utf-8

import types
import unittest

import sonos
import upnp


# Output from my Sonos system, with UUIDs sanitized.
ACTUAL_TOPOLOGY_XML = (
    '&lt;ZoneGroups&gt;&lt;ZoneGroup Coordinator=&quot;RINCON_5CAA000000000000'
    '1&quot; ID=&quot;RINCON_5CAA0000000000001:13&quot;&gt;&lt;ZoneGroupMember'
    ' UUID=&quot;RINCON_5CAA0000000000001&quot; Location=&quot;http://192.168.'
    '1.100:1400/xml/device_description.xml&quot; ZoneName=&quot;Michael&amp;ap'
    'os;s Room&quot; Icon=&quot;x-rincon-roomicon:living&quot; Configuration=&'
    'quot;1&quot; SoftwareVersion=&quot;34.7-33240-Wilco_Release&quot; MinComp'
    'atibleVersion=&quot;33.0-00000&quot; LegacyCompatibleVersion=&quot;25.0-0'
    '0000&quot; BootSeq=&quot;13&quot; WirelessMode=&quot;1&quot; WirelessLeaf'
    'Only=&quot;0&quot; HasConfiguredSSID=&quot;1&quot; ChannelFreq=&quot;2437'
    '&quot; BehindWifiExtender=&quot;0&quot; WifiEnabled=&quot;1&quot; Orienta'
    'tion=&quot;0&quot; RoomCalibrationState=&quot;4&quot; SecureRegState=&quo'
    't;3&quot;/&gt;&lt;/ZoneGroup&gt;&lt;ZoneGroup Coordinator=&quot;RINCON_B8'
    'E90000000000002&quot; ID=&quot;RINCON_B8E90000000000002:67&quot;&gt;&lt;Z'
    'oneGroupMember UUID=&quot;RINCON_B8E90000000000002&quot; Location=&quot;h'
    'ttp://192.168.1.67:1400/xml/device_description.xml&quot; ZoneName=&quot;L'
    'iving Room&quot; Icon=&quot;x-rincon-roomicon:living&quot; Configuration='
    '&quot;1&quot; SoftwareVersion=&quot;34.7-33240-Wilco_Release&quot; MinCom'
    'patibleVersion=&quot;33.0-00000&quot; LegacyCompatibleVersion=&quot;25.0-'
    '00000&quot; BootSeq=&quot;92&quot; WirelessMode=&quot;1&quot; WirelessLea'
    'fOnly=&quot;0&quot; HasConfiguredSSID=&quot;1&quot; ChannelFreq=&quot;243'
    '7&quot; BehindWifiExtender=&quot;0&quot; WifiEnabled=&quot;1&quot; Orient'
    'ation=&quot;0&quot; RoomCalibrationState=&quot;4&quot; SecureRegState=&qu'
    'ot;3&quot;/&gt;&lt;/ZoneGroup&gt;&lt;ZoneGroup Coordinator=&quot;RINCON_B'
    '8E90000000000003&quot; ID=&quot;RINCON_B8E90000000000003:49&quot;&gt;&lt;'
    'ZoneGroupMember UUID=&quot;RINCON_B8E90000000000003&quot; Location=&quot;'
    'http://192.168.1.69:1400/xml/device_description.xml&quot; ZoneName=&quot;'
    'Dining Room&quot; Icon=&quot;x-rincon-roomicon:dining&quot; Configuration'
    '=&quot;1&quot; SoftwareVersion=&quot;34.7-33240-Wilco_Release&quot; MinCo'
    'mpatibleVersion=&quot;33.0-00000&quot; LegacyCompatibleVersion=&quot;25.0'
    '-00000&quot; BootSeq=&quot;113&quot; WirelessMode=&quot;1&quot; WirelessL'
    'eafOnly=&quot;0&quot; HasConfiguredSSID=&quot;1&quot; ChannelFreq=&quot;2'
    '437&quot; BehindWifiExtender=&quot;0&quot; WifiEnabled=&quot;1&quot; Orie'
    'ntation=&quot;0&quot; RoomCalibrationState=&quot;4&quot; SecureRegState=&'
    'quot;3&quot;/&gt;&lt;/ZoneGroup&gt;&lt;/ZoneGroups&gt;'
)
ACTUAL_TOPOLOGY_PARSED = [
    {
        'coordinator_uuid': 'RINCON_5CAA0000000000001',
        'players': {
            'RINCON_5CAA0000000000001': {
                'ip': '192.168.1.100',
                'name': 'Michael\'s Room',
                'uuid': 'RINCON_5CAA0000000000001'
            }
        }
    },
    {
        'coordinator_uuid': 'RINCON_B8E90000000000002',
        'players': {
            'RINCON_B8E90000000000002': {
                'ip': '192.168.1.67',
                'name': 'Living Room',
                'uuid': 'RINCON_B8E90000000000002'
            }
        }
    },
    {
        'coordinator_uuid': 'RINCON_B8E90000000000003',
        'players': {
            'RINCON_B8E90000000000003': {
                'ip': '192.168.1.69',
                'name': 'Dining Room',
                'uuid': 'RINCON_B8E90000000000003'
            }
        }
    }
]


class ZoneGroupTopologyTests(unittest.TestCase):

    def test_location_to_ip(self):
        """Given a Location from a Zone Group Topology we can get the IP of the player."""
        location = 'http://192.168.1.69:1400/xml/device_description.xml'
        ip = sonos._zone_group_topology_location_to_ip(location)
        self.assertEqual(ip, '192.168.1.69')

    # Would have prefered contextlib.contextmanager, but pip-micropython
    # seems to have issues with it.
    # Obviously would have preferred unittest.mock if it were available.
    class _mock:
        def __init__(self, owner, method_name, return_value):
            self.owner = owner
            self.method_name = method_name
            self.return_value = return_value
        def __enter__(self):
            # MicroPython's unittest doesn't have a mock module.
            def mocked(*args, **kwargs):
                return self.return_value
            self.original = getattr(self.owner, self.method_name)
            setattr(self.owner, self.method_name, mocked)
        def __exit__(self, *unused):
            setattr(self.owner, self.method_name, self.original)

    def test_zone_group_topology(self):
        """Parsing the Zone Group State from my local network gives the right output."""
        resp_arguments = {'ZoneGroupState': ACTUAL_TOPOLOGY_XML}
        with self._mock(upnp, 'send_command', resp_arguments):
            topology = sonos.query_zone_group_topology('0.0.0.0')
        self.assertEqual(topology, ACTUAL_TOPOLOGY_PARSED)

    def test_discover_actual_topology(self):
        """Given a topology, sonos.discover() should return Sonos instances for
        each speaker in the network."""
        with self._mock(sonos, '_discover_ip', '0.0.0.0'):
            with self._mock(sonos, 'query_zone_group_topology', ACTUAL_TOPOLOGY_PARSED):
                speakers = sonos.discover()
                self.assertIsInstance(speakers, types.GeneratorType)
                speakers = list(speakers)
                # Despite the name, this built-in method actually checks the
                # lists are equal, without caring about order.
                self.assertCountEqual(speakers, [
                    sonos.Sonos('RINCON_5CAA0000000000001', '192.168.1.100', 'Michael\'s Room'),
                    sonos.Sonos('RINCON_B8E90000000000002', '192.168.1.67', 'Living Room'),
                    sonos.Sonos('RINCON_B8E90000000000003', '192.168.1.69', 'Dining Room'),
                ])

    def test_discover_fake_topology_with_two_speakers_in_group(self):
        """sonos.discover() should return one Sonos instance per group, with the
        other members of the group available from that instance."""
        FAKE_TOPOLOGY_PARSED = [{
            'coordinator_uuid': 'RINCON_5CAA0000000000001',
            'players': {
                'RINCON_5CAA0000000000001': {
                    'ip': '192.168.1.100',
                    'name': 'Michael\'s Room',
                    'uuid': 'RINCON_5CAA0000000000001'
                },
                'RINCON_B8E90000000000002': {
                    'ip': '192.168.1.67',
                    'name': 'Living Room',
                    'uuid': 'RINCON_B8E90000000000002'
                }
            }
        }]
        with self._mock(sonos, '_discover_ip', '0.0.0.0'):
            with self._mock(sonos, 'query_zone_group_topology', FAKE_TOPOLOGY_PARSED):
                speakers = list(sonos.discover())
                self.assertEqual(speakers, [
                    sonos.Sonos('RINCON_5CAA0000000000001', '192.168.1.100', 'Michael\'s Room'),
                ])
                self.assertEqual(speakers[0].other_players, [
                    sonos.Sonos('RINCON_B8E90000000000002', '192.168.1.67', 'Living Room'),
                ])


if __name__ == '__main__':
    unittest.main()
