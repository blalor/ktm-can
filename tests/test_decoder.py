# -*- encoding: utf-8 -*-

from ktm_can.decoder import Decoder, Message
import os
import struct

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def pack_data(*data):
    return struct.pack("8B", *data)


def make_msg(bytes_str):
    rec = bytes_str.split(",")
    return Message(int(rec[0], 16), pack_data(*[ int(d, 16) for d in rec[1:] ]))


def decode(decoder, msg):
    parsed = {}
    for sender, key, value in decoder.decode(msg):
        parsed[sender, key] = value

    return parsed


class TestDecoder(object):
    decoder = Decoder()

    def test_120(self, tmpdir):
        parsed = decode(self.decoder, make_msg("120,06,79,00,00,00,00,00,3F"))

        assert len(parsed) == 4
        assert parsed[0x120, "rpm"] == 1657
        assert parsed[0x120, "throttle"] == 0
        assert parsed[0x120, "kill_switch"] == 0
        assert parsed[0x120, "throttle_map"] == 0

    def test_129(self, tmpdir):
        parsed = decode(self.decoder, make_msg("129,30,00,00,00,00,00,00,30"))

        assert len(parsed) == 2
        assert parsed[0x129, "gear"] == 3
        assert parsed[0x129, "clutch"] == 0