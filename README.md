This repository contains a Python library for parsing CAN bus messages from KTM motorcycles.  It's intended to be documentation and a reference implementation that can be used to build real applications.

There are a few things I'd like to explore, but it provides all the data I need for my project at this point.  I'm happy to accept contributions for additional message parsing and vehicle support, however.

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

Utility scripts are included in the `scripts` directory; I use these while working with live data and captured logs, mainly to verify functionality and to identify data that corresponds with actions (like turning a wheel or pressing a button).  They're rough because I mainly use them as live debugging aids, tweaking the source to filter out messages I'm not interested in, reduce noise, etc.  Several of them depend on [python-can](https://python-can.readthedocs.io/en/master/) for reading live data.

## message id overview

| CAN ID | Speed (ms) | Provides                                                 | Model(s)       |
|--------|------------|----------------------------------------------------------|----------------|
| `120`  | 20         | engine rpm, throttle position, kill switch, throttle map | 690 Enduro R   |
| `129`  | 20         | gear position, clutch switch                             | 690 Enduro R   |
| `12A`  | 50         | throttle map (requested), throttle state                 | 690 Enduro R   |
| `12B`  | 10         | front wheel speed, rear wheel speed, lean, tilt angles   | 690 Enduro R   |
| `290`  | 10         | front brake pressure                                     | 690 Enduro R   |
| `450`  | 50         | traction control button                                  | 690 Enduro R   |
| `540`  | 100        | engine rpm, gear, side stand switch, coolant temp        | 690 Enduro R   |

## developing

0. clone this repo
1. create a virtual environment: `python3 -m venv .env`
2. activate the virualenv: `. .env/bin/activate`
3. install development dependencies: `pip install -r dev_requirements.txt`
4. install source for local development: `python3 setup.py develop`
5. make changes
6. run tests: `pytest`

## hardware

If you want to get on the (CAN) bus, you need some hardware. The following are what I used to connect to the KTM diagnostic port and access the data from my laptop:

* 6-pin Sumitomo MT 090 male connector (p/n [6189-6171](http://prd.sws.co.jp/components/en/detail.php?number_s=61896171))
* 4 terminals [8230-4408](http://prd.sws.co.jp/components/en/detail.php?number_s=82304408) or [1500-0105](http://prd.sws.co.jp/components/en/detail.php?number_s=15000105), depending on wire size
* 4 wire seals [7160-8234](http://prd.sws.co.jp/components/en/detail.php?number_s=71608234)
* 2 dummy plugs [7160-9465](http://prd.sws.co.jp/components/en/detail.php?number_s=71609465)
* wire (duh?)
* [USB-to-CAN adapter](https://www.seeedstudio.com/USB-CAN-Analyzer-p-2888.html)

I purchased the connectors from [Cycle Terminal](http://www.cycleterminal.com/mt-series-090.html).

## contributing

The current state of things is far from complete and only represents data confirmed from my own 2020 KTM 690 Enduro R. The original work decoding the messages was done in 2017 for a SuperDuke 1290: I've (obviously?) not made any attempts to verify that this code works with messages from that bike or other bikes, but I have ideas for extending things to support other models even if not all messages are the same.  I welcome contributions in the form of pull requests and issues (even if it's just a question!).
