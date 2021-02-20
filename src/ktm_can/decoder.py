# -*- encoding: utf-8 -*-

## decodes messages read from the KTM CaAN bus

import struct


class Message(object):
    """a message read from the bus"""
    def __init__(self, sender_id, data):
        super(Message, self).__init__()
        self.id = sender_id
        self.data = data


class Decoder(object):
    """decoder of Message objects"""
    def __init__(self, emit_unmapped=False):
        super(Decoder, self).__init__()

        self.emit_unmapped = emit_unmapped

    def decode(self, msg):
        """yields (id, key, value) tuples for known data in a Message"""

        if msg.id == 0x120:
            ## D0, D1 -- engine rpm
            yield msg.id, "rpm", struct.unpack(">H", msg.data[0:2])[0]

            ## D2 -- (commanded?) throttle;
            ## @todo confirm range; assumed to be 0-255
            yield msg.id, "throttle", msg.data[2]

            ## D3 B4 -- kill switch position
            yield msg.id, "kill_switch", (msg.data[3] & 0b00010000) >> 4

            ## D4, B7 -- throttle map
            ## @todo determine if requested or actual
            yield msg.id, "throttle_map", msg.data[4] & 0b00000001

            ## D5 -- unknown
            ## D6 -- unknown
            ## D7 -- counter

            ## no additional usable data found
            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "__",
                    "__",
                    "__",
                    "{:02X}".format(msg.data[3] & (~0b00010000 & 0xFF)),
                    "{:02X}".format(msg.data[4] & (~0b00000001 & 0xFF)),
                    "{:02X}".format(msg.data[5]),
                    "{:02X}".format(msg.data[6]),
                    "__", # "{:02X}".format(msg.data[7]),              ## counter?
                ])
