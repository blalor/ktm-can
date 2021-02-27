# -*- encoding: utf-8 -*-

## decodes messages read from the KTM CAN bus

import struct


def lo_nibble(b):
    return b & 0x0F


def hi_nibble(b):
    return (b >> 4) & 0x0F


def signed12(value):
    return -(value & 0b100000000000) | (value & 0b011111111111)


def invert(value):
    return (~value & 0xFF)


class Decoder(object):
    """decoder of Message objects"""
    def __init__(self, emit_unmapped=False):
        super(Decoder, self).__init__()

        self.emit_unmapped = emit_unmapped

    def decode(self, msg):
        """yields (id, key, value) tuples for known data in a Message"""

        if msg.id == 0x120:
            ## Received every 20ms

            ## D0, D1 -- engine rpm
            yield msg.id, "rpm", struct.unpack(">H", msg.data[0:2])[0]

            ## D2 -- (commanded) throttle; range 0-255
            yield msg.id, "throttle", msg.data[2]

            ## D3 B4 -- kill switch position
            ## run == 1, stop == 0
            yield msg.id, "kill_switch", (msg.data[3] & 0b00010000) >> 4

            ## D4, B7 -- throttle map, actual
            yield msg.id, "throttle_map", msg.data[4] & 0b00000001

            ## D5 -- unknown
            ## D6 -- unknown
            ## D7 -- counts through 30, 50, 70, 90, B0, D0, repeats

            ## no additional usable data found
            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "__",
                    "__",
                    "__",
                    "{:02X}".format(msg.data[3] & invert(0b00010000)),
                    "{:02X}".format(msg.data[4] & invert(0b00000001)),
                    "{:02X}".format(msg.data[5]),
                    "{:02X}".format(msg.data[6]),
                    "__",
                ])

        elif msg.id == 0x129:
            ## Received every 20ms

            ## D0, B0..B4 -- gear position; 0 is neutral
            yield msg.id, "gear", hi_nibble(msg.data[0])

            ## D0, B5 -- clutch switch
            yield msg.id, "clutch_in", ((msg.data[0] & 0b00001000) >> 3) == 1

            ## D1 -- unknown
            ## D2 -- unknown
            ## D3 -- unknown
            ## D4 -- unknown
            ## D5 -- unknown
            ## D6 -- unknown
            ## D7 -- counts through 20, 40, 60, 80, A0, C0, repeats

            ## no additional usable data found
            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "__",
                    "{:02X}".format(msg.data[1]),
                    "{:02X}".format(msg.data[2]),
                    "{:02X}".format(msg.data[3]),
                    "{:02X}".format(msg.data[4]),
                    "{:02X}".format(msg.data[5]),
                    "{:02X}".format(msg.data[6]),
                    "__",
                ])

        elif msg.id == 0x12A:
            ## Received every 50ms

            ## D0 -- throttle open/closed
            ## 10 when throttle rises to 4, 12 when throttle goes back down to 3
            ## probably connected to the map selection, which only changes when
            ## the throttle is closed.
            yield msg.id, "throttle_open", (msg.data[0] & 0b00000010) >> 1 == 0

            ## D1, B1 -- requested throttle map: 0 == mode 1, 1 == mode 2
            yield msg.id, "requested_throttle_map", (msg.data[1] & 0b01000000) >> 6

            ## D1, B2 -- seems to be set to 1 after key turned on and ECU is
            ## initialized(?) also flips when engine is started, but returns to
            ## 1 when running

            ## D2 -- always 0
            assert msg.data[2] == 0

            ## D3 -- unknown

            ## D4..D8 -- always 0
            assert msg.data[4] == 0
            assert msg.data[5] == 0
            assert msg.data[6] == 0
            assert msg.data[7] == 0

            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "{:02X}".format(msg.data[0] & invert(0b00000010)),
                    "{:02X}".format(msg.data[1] & invert(0b01000000)),
                    "__", # "{:02X}".format(msg.data[2]),
                    "{:02X}".format(msg.data[3]),
                    "__", # "{:02X}".format(msg.data[4]),
                    "__", # "{:02X}".format(msg.data[5]),
                    "__", # "{:02X}".format(msg.data[6]),
                    "__", # "{:02X}".format(msg.data[7]),
                ])

        elif msg.id == 0x12B:
            ## Received every 10ms

            ## D0..D1  -- front wheel speed
            ## D2..D3 -- rear wheel speed
            front_wheel, rear_wheel = struct.unpack(">HH", msg.data[0:4])
            yield msg.id, "front_wheel", front_wheel
            yield msg.id, "rear_wheel", rear_wheel

            ## D4 -- unknown

            ## D5..D7 -- lean angle, tilt
            ## from Dan Plastina:
            #> Lean Angle – it’s provided by ID 299. The last 3 bytes (6,7,8)
            #> split into two 12bit counters. The last 0x000 is for lean. I’ve
            #> tested the lean extensively. 0x000 is neutral, 0x001 starts
            #> leaning to the right. 0xFFF starts leaning to the left. I
            #> *believe* the first 0x000 are tilt but I’ve yet to validate.

            ## this looks like a 12-bit two's complement signed integer
            ## https://stackoverflow.com/a/32262478/53051

            yield msg.id, "tilt", signed12((msg.data[5] << 4) | hi_nibble(msg.data[6]))
            yield msg.id, "lean", signed12((lo_nibble(msg.data[6]) << 8) | msg.data[7])

            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "__", # "{:02X}".format(msg.data[0]),
                    "__", # "{:02X}".format(msg.data[1]),
                    "__", # "{:02X}".format(msg.data[2]),
                    "__", # "{:02X}".format(msg.data[3]),
                    "{:02X}".format(msg.data[4]),
                    "__", # "{:02X}".format(msg.data[5]),
                    "__", # "{:02X}".format(msg.data[6]),
                    "__", # "{:02X}".format(msg.data[7]),
                ])

        elif msg.id == 0x450:
            # Received every 50ms

            ## D0, D1 -- always 0
            assert msg.data[0] == 0
            assert msg.data[1] == 0

            ## D2
            yield msg.id, "traction_control_button", msg.data[2] & 0b00000001

            ## D3 -- always 0
            assert msg.data[3] == 0

            ## D4 -- toggles between 0x00 and 0x09 when map button released; 09 for requesting map 1, 00 for requesting map 0
            # 450                                  | __ __ 00 __ 09 __ __ __
            # 12A requested_throttle_map           | 1
            # 450                                  | __ __ 00 __ 00 __ __ __
            # 12A requested_throttle_map           | 0
            ## so looks like similar data, different place.
            ## skipping parsing here because I feel like there are two bits
            ## masquerading as a single value, which seems weird.

            ## D5..D7 -- always 0
            assert msg.data[5] == 0
            assert msg.data[6] == 0
            assert msg.data[7] == 0

            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "__",
                    "__",
                    "{:02X}".format(msg.data[2] & 0b11111110),
                    "__",
                    "{:02X}".format(msg.data[4]),
                    "__",
                    "__",
                    "__",
                ])

        elif msg.id == 0x540:
            ## Received every 100ms

            ## D0 -- always 0x02
            assert msg.data[0] == 0x02

            ## D1, D2 -- engine rpm; as 0x120, but updated more slowly
            yield msg.id, "rpm", struct.unpack(">H", msg.data[1:3])[0]

            ## D3 -- also gear position (lo nibble)
            ## 7 if unknown! so maybe QS-related?
            yield msg.id, "gear", lo_nibble(msg.data[3])

            ## D4 -- kickstand (1 is raised), kickstand error
            yield msg.id, "kickstand_up", (msg.data[4] & 0b00000001) == 1
            yield msg.id, "kickstand_err", ((msg.data[4] & 0b10000000) >> 7) == 1

            ## D4, B3 -- 1 key on, kill switch on, not running; 0 after start;
            ## returns to 1 after killing engine with kill switch and returning
            ## to run position.

            ## D5 -- always 0x00
            assert msg.data[5] == 0x00

            ## D6 -- engine coolant, °C; compared to OBD2 value
            yield msg.id, "coolant_temp", struct.unpack(">H", msg.data[6:])[0] / 10.0

            if self.emit_unmapped:
                yield msg.id, "unmapped", " ".join([
                    "__",
                    "__",
                    "__",
                    "{:02X}".format(hi_nibble(msg.data[3])),
                    "{:02X}".format(msg.data[4] & 0b01111110),
                    "__",
                    "__",
                    "__",
                ])
