#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
import can
from ktm_can.decoder import Decoder

## reads live data from a can interface, emits decoded messages to stdout when
## they change


class MsgAdapter(object):
    """Adapts can messages to what the ktm_can decoder needs"""
    def __init__(self, msg):
        super(MsgAdapter, self).__init__()
        self.msg = msg

    @property
    def id(self):
        return self.msg.arbitration_id

    @property
    def data(self):
        return self.msg.data


def main(device_path):
    bus = can.Bus(device_path, interface="seeedstudio")
    decoded_msgs = {}
    decoder = Decoder(emit_unmapped=True, enable_assertions=True)

    try:
        while True:
            msg = bus.recv(timeout=1.0 / 1000.0)
            if msg is None:
                continue

            for msg_id, key, value in decoder.decode(MsgAdapter(msg)):
                # if (msg_id, key) in (
                #     (0x120, "rpm"),
                #     (0x120, "throttle"),
                #     (0x120, "kill_switch"),
                #     (0x120, "throttle_map"),
                #     # (0x129, "gear"),
                #     (0x129, "clutch_in"),
                #     (0x12A, "requested_throttle_map"),
                #     (0x12B, "front_wheel"),
                #     (0x12B, "rear_wheel"),
                #     (0x12B, "tilt"),
                #     (0x12B, "lean"),
                #     (0x290, "front_brake"),
                #     (0x450, "traction_control_button"),
                #     (0x540, "rpm"),
                #     (0x540, "gear"),
                #     (0x540, "kickstand_up"),
                #     (0x540, "kickstand_err"),
                #     (0x540, "coolant_temp"),
                # ):
                #     continue

                if key == "unmapped":
                    key = ""

                old_val = decoded_msgs.get((msg_id, key), None)
                if old_val != value:
                    print("{:03X} {:32} | {}".format(msg_id, key, value))

                decoded_msgs[msg_id, key] = value

    except Exception:
        bus.shutdown()
        raise


if __name__ == "__main__":
    main(*sys.argv[1:])
