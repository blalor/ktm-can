# -*- encoding: utf-8 -*-

from ktm_can.decoder import Decoder
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


class Message(object):
    """a message read from the bus"""
    def __init__(self, sender_id, data):
        super(Message, self).__init__()
        self.id = sender_id
        self.data = data


class TestDecoder(object):
    decoder = Decoder()

    def test_120(self):
        parsed = decode(self.decoder, make_msg("120,06,79,00,00,00,00,00,3F"))

        assert len(parsed) == 4
        assert parsed[0x120, "rpm"] == 1657
        assert parsed[0x120, "throttle"] == 0
        assert parsed[0x120, "kill_switch"] == 0
        assert parsed[0x120, "throttle_map"] == 0

    def test_129(self):
        parsed = decode(self.decoder, make_msg("129,30,00,00,00,00,00,00,30"))

        assert len(parsed) == 2
        assert parsed[0x129, "gear"] == 3
        assert parsed[0x129, "clutch_in"] is False

    def test_12A_map1(self):
        parsed = decode(self.decoder, make_msg("12A,11,28,00,20,00,00,00,00"))

        assert len(parsed) == 2
        assert parsed[0x12A, "requested_throttle_map"] == 0
        assert parsed[0x12A, "throttle_open"] is True

    def test_12A_map2(self):
        parsed = decode(self.decoder, make_msg("12A,13,68,00,20,00,00,00,00"))

        assert len(parsed) == 2
        assert parsed[0x12A, "requested_throttle_map"] == 1
        assert parsed[0x12A, "throttle_open"] is False

    def test_12B(self):
        parsed = decode(self.decoder, make_msg("12B,00,00,02,16,00,02,8F,FD"))

        assert len(parsed) == 4
        assert parsed[0x12B, "front_wheel"] == 0 ## @todo better sample
        assert parsed[0x12B, "rear_wheel"] == 534
        assert parsed[0x12B, "tilt"] == 40
        assert parsed[0x12B, "lean"] == -3

    def test_450(self):
        parsed = decode(self.decoder, make_msg("450,00,00,01,00,00,00,00,00"))

        assert len(parsed) == 1
        assert parsed[0x450, "traction_control_button"] == 1

    def test_540(self):
        parsed = decode(self.decoder, make_msg("540,02,06,65,00,01,00,01,DD"))

        assert len(parsed) == 5
        assert parsed[0x540, "rpm"] == 1637
        assert parsed[0x540, "kickstand_up"] is True
        assert parsed[0x540, "kickstand_err"] is False
        assert parsed[0x540, "coolant_temp"] == 47.7
        assert parsed[0x540, "gear"] == 0

    def test_540_gear7(self):
        parsed = decode(self.decoder, make_msg("540,02,06,AA,07,01,00,01,5B"))

        assert len(parsed) == 5
        assert parsed[0x540, "rpm"] == 1706
        assert parsed[0x540, "kickstand_up"] is True
        assert parsed[0x540, "kickstand_err"] is False
        assert parsed[0x540, "coolant_temp"] == 34.7
        assert parsed[0x540, "gear"] == 7
