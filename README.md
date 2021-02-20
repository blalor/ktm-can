This repository contains a Python library for parsing CAN bus messages from KTM motorcycles.  It's intended to be documentation and a reference implementation that can be used to build real applications.

It's still very much a work in progress, both in structure and content.

Credit for the original decoding goes to [Dan Plastina](https://advrider.com/f/members/dan-plastina.12530/) who documented his work in a [thread on advrider.com](https://advrider.com/f/threads/results-from-hacking-the-ktm-superduke-1290-can-bus.1200087/)

## CAN bus message structure

Messages contain an ID and 8 bytes of data, referenced by their indices.  Values are represented in hex.

```
    |                           CAN message                         |
    | CANID |                       CAN data                        |
    |  ID0  |  D0  |  D1  |  D2  |  D3  |  D4  |  D5  |  D6  |  D7  |
```

Each byte contains 8 bits.

```
            |                          byte                         |
    bits →  |  B0  |  B1  |  B2  |  B3  |  B4  |  B5  |  B6  |  B7  |
            |         high nibble       |         low nibble        |
```

## repository structure

Module source is in [`src/ktm_can/decoder.py`](src/ktm_can/decoder.py).  Tests are in the `tests` directory, and are intended to document raw message structure being parsed by the library and validated against known-good values.
