#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
import csv
import struct
from ktm_can.decoder import Decoder

## parses CSV data with the following structure:
## Timestamp,ID,Data0,Data1,Data2,Data3,Data4,Data5,Data6,Data7,
##
## emits parsed messages to stdout


class Message(object):
    def __init__(self, dev_id, data):
        self.id = dev_id
        self.data = data


def pack_data(*data):
    return struct.pack("8B", *data)


def make_msg(csv_str):
    rec = csv_str.split(",")
    return Message(int(rec[0], 16), pack_data(*[ int(d, 16) for d in rec[1:] ]))


class DictOnChangeNotifier(dict):
    def __init__(self, notifier):
        self.__notifier = notifier

        super(DictOnChangeNotifier, self).__init__()

    def __setitem__(self, name, value):
        old_val = self.get(name, None)
        if old_val != value:
            super(DictOnChangeNotifier, self).__setitem__(name, value)
            self.__notifier(name, value)


def main(fn=None):
    if fn is None:
        ifp = sys.stdin
    else:
        ifp = open(fn)

    reader = csv.reader(ifp)

    decoded_msgs = DictOnChangeNotifier(lambda k, v: print("{:03X} {:32} | {}".format(k[0], k[1], v)))

    decoder = Decoder(emit_unmapped=True)

    for rec in reader:
        # ts = rec[0]
        try:
            msg = make_msg(",".join(rec[1:]))
        except ValueError:
            continue

        if msg.id in (0x12B,):
            continue

        for msg_id, key, value in decoder.decode(msg):
            if key in ("rpm", "coolant_temp", "throttle"):
                continue

            decoded_msgs[msg_id, key] = value

    if fn is not None:
        ifp.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
