#!/usr/bin/env python
# encoding: utf-8

import urequests
import xmltok


soap_action_template = 'urn:schemas-upnp-org:service:{service_type}:{version}#{action}'
soap_body_template = (
    '<?xml version="1.0"?>'
    '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"'
    ' s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
        '<s:Body>'
            '<u:{action} xmlns:u="urn:schemas-upnp-org:service:'
                '{service_type}:{version}">'
                '{arguments}'
            '</u:{action}>'
        '</s:Body>'
    '</s:Envelope>'
)


def parse_response(action, resp):
    arguments = []
    action_response_tag = ('u', action + 'Response')

    # We want to look for a tag <u:{action}Response>, and produce a list of
    # ({name}, {value}) tuples, for each <{name}>{value}</{name}> child element
    # of it. Rather than use a proper parser, use the MicroPython XML tokenizer.
    tokens = xmltok.tokenize(resp.raw)
    token = token_value = None
    try:
        while not (token == xmltok.START_TAG and token_value == action_response_tag):
            token, token_value, *_ = next(tokens)

        argument_name = None
        while not (token == xmltok.END_TAG and token_value == action_response_tag):
            token, token_value, *_ = next(tokens)
            # This will produce some screwy results on dodgy input, but it's
            # nice and simple.
            if token == xmltok.START_TAG:
                _, argument_name = token_value
            elif token == xmltok.TEXT:
                arguments.append((argument_name, token_value))
                argument_name = None
    except StopIteration:
        raise Exception('Bad UPnP response')

    return arguments


def send_command(url, service_type, version, action, arguments):
    # NOTE: Does not deal with any escaping.
    wrapped_arguments = ''.join(
        '<{name}>{value}</{name}>'.format(name=name, value=value)
        for name, value in arguments
    )
    soap = soap_body_template.format(
        service_type=service_type, version=version, action=action,
        arguments=wrapped_arguments
    ).encode('utf-8')
    soap_action = soap_action_template.format(
        service_type=service_type, version=version, action=action,
    )
    headers = {
        'Content-Type': 'text/xml; charset="utf-8"',
        'SOAPACTION': soap_action,
    }

    resp = urequests.post(url, headers=headers, data=soap)


# url = '192.168.1.100'
# send_upnp_command(
#     'http://{url}:1400/MediaRenderer/AVTransport/Control'.format(url=url),
#     'AVTransport', 1, 'Pause', [('InstanceID', 0), ('Speed', 1)]
# )
