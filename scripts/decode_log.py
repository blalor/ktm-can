#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
import csv
import struct
from ktm_can.decoder import Decoder

## parses CSV data (from a file or stdin) with the following structure:
## Timestamp,ID,Data0,Data1,Data2,Data3,Data4,Data5,Data6,Data7,
##
## emits parsed messages to stdout when they change


class Message(object):
    def __init__(self, dev_id, data):
        self.id = dev_id
        self.data = data


def pack_data(*data):
    return struct.pack("8B", *data)


def make_msg(csv_str):
    rec = csv_str.split(",")
    return Message(int(rec[0], 16), pack_data(*[ int(d, 16) for d in rec[1:] ]))


def main(fn=None):
    if fn is None:
        ifp = sys.stdin
    else:
        ifp = open(fn)

    reader = csv.reader(ifp)

    decoded_msgs = {}

    decoder = Decoder(emit_unmapped=True, enable_assertions=True)

    for rec in reader:
        try:
            ts = int(rec[0])
            msg = make_msg(",".join(rec[1:]))
        except ValueError:
            continue

        # if msg.id in (0x12B,):
        #     continue

        for msg_id, key, value in decoder.decode(msg):
            # if key in (
            #     # "rpm",
            #     "coolant_temp",
            #     # "throttle",
            #     "lean?",
            #     "tilt?",
            # ):
            #     continue

            if key == "unmapped":
                key = ""

            old_val = decoded_msgs.get((msg_id, key), None)
            if old_val != value:
                print("{:-6d} {:03X} {:32} | {}".format(ts, msg_id, key, value))

            decoded_msgs[msg_id, key] = value

    if fn is not None:
        ifp.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
