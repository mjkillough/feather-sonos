#!/usr/bin/env python
# encoding: utf-8

import unittest

try:
    import uio as io
except ImportError:
    import io

import upnp


class UpnpTests(unittest.TestCase):

    soap_response_template = (
        '<?xml version="1.0"?>'
        '<s:Envelope '
            'xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
            's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            '<s:Body>'
                '<u:{action}Response xmlns:u="urn:schemas-upnp-org:service:serviceType:v">'
                    '{args_xml}'
                '</u:{action}Response>'
            '</s:Body>'
        '</s:Envelope>'
    )
    argument_temlate = '<{name}>{value}</{name}>'

    def test_parse_response_no_arguments(self):
        """Passing a SOAP response with no arguments should give []"""
        soap_xml = self.soap_response_template.format(
            action='Pause', args_xml=''
        )
        arguments = upnp.parse_response('Pause', io.StringIO(soap_xml))
        self.assertEqual(arguments, dict())

    def test_parse_response_with_arguments(self):
        """Passing a SOAP response with some valid arguments should return them"""
        args = [
            dict(name='arg1', value='value1'),
            dict(name='arg2', value='value2'),
        ]
        args_xml = ''.join(
            self.argument_temlate.format(**arg)
            for arg in args
        )
        soap_xml = self.soap_response_template.format(
            action='Pause', args_xml=args_xml
        )
        arguments = upnp.parse_response('Pause', io.StringIO(soap_xml))
        self.assertEqual(arguments, dict([
            (arg['name'], arg['value'])
            for arg in args
        ]))

    def test_parse_response_with_invalid_xml(self):
        """Passing some invalid badly formed XML should cause it to give up"""
        with self.assertRaises(Exception):
            upnp.parse_response('Pause', io.StringIO('<a>'))

    def test_unescape_special_characters(self):
        """Argument values should have their special characters unescaped"""
        arg = dict(name='arg1', value='&lt;xml attr=&quot;with &amp;apos; in it&quot;&gt;&lt;/test&gt;')
        args_xml = self.argument_temlate.format(**arg)
        soap_xml = self.soap_response_template.format(
            action='NotReal', args_xml=args_xml
        )
        arguments = upnp.parse_response('NotReal', io.StringIO(soap_xml))
        self.assertEqual(arguments, dict(arg1='<xml attr="with \' in it"></test>'))

if __name__ == '__main__':
    unittest.main()
