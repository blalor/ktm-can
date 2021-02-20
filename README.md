This repository contains a Python library for parsing CAN bus messages from KTM motorcycles.  It's intended to be documentation and a reference implementation that can be used to build real applications.

It's still very much a work in progress, both in structure and content.

Credit for the original decoding goes to [Dan Plastina](https://advrider.com/f/members/dan-plastina.12530/) who documented his work in a [thread on advrider.com](https://advrider.com/f/threads/results-from-hacking-the-ktm-superduke-1290-can-bus.1200087/). Additional details have been included from others posting in that same thread.

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

Module source is in [`src/ktm_can/decoder.py`](src/ktm_can/decoder.py).  Tests are in the `tests` directory, and are intended to document raw message structure being parsed by the library and validated against known-good values.  The tests should give you a good idea of the data that's available, and the source contains comments with additional details, such as message frequency, assumptions about valid data, etc.

## message id overview

| CAN ID          | Speed (ms) | Provides                                              | Model(s)       |
|-----------------|------------|-------------------------------------------------------|----------------|
| [`120`](120.md) | 20         | Engine RPM, throttle, kill switch, throttle map       | 690 Enduro R   |
| [`129`](129.md) | 20         | Gear position, clutch switch                          | 690 Enduro R   |
| [`12A`](12A.md) | 50         | Throttle map (requested)                              | 690 Enduro R   |
| [`12B`](12B.md) | 10         | Front wheel speed, rear wheel speed, lean, tilt angle | 690 Enduro R   |
| [`450`](450.md) | 50         | Traction control button                               | 690 Enduro R   |
| [`540`](540.md) | 100        | Engine RPM, Side stand switch, coolant temp           | 690 Enduro R   |

## developing

0. clone this repo
1. create a virtual environment: `python3 -m venv .env`
2. activate the virualenv: `. .env/bin/activate`
3. install development dependencies: `pip install -r dev_requirements.txt`
4. install source for local development: `python3 setup.py develop`
5. make changes
6. run tests: `pytest`

## contributing

The current state of things is far from complete and only represents data confirmed from my own 2020 KTM 690 Enduro R. The original work decoding the messages was done in 2017 for a SuperDuke 1290: I've (obviously?) not made any attempts to verify that this code works with messages from that bike or other bikes, but I have ideas for extending things to support other models even if not all messages are the same.  I welcome contributions in the form of pull requests and issues (even if it's just a question!).
