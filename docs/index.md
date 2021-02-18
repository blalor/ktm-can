This repository documents KTM CAN messages     
        
[Online Discussion Forum](https://advrider.com/f/threads/results-from-hacking-the-ktm-superduke-1290-can-bus.1200087/ )

Repo format inspred by https://docs.google.com/spreadsheets/d/1tUrOES5fQZa92Robr6uP8v2dzQDq9ohHjUiTU3isqdc/edit#gid=1224172550
        
Contributors:

* Brian Lalor -- Librarian, originator of this document. 2020 KTM 690 Enduro R
* [Dan Plastina](https://advrider.com/f/members/dan-plastina.12530/) -- Thread ☝️ starter; KTM SuperDuke 1290

## key

```
    |                           CAN message                         |
    | CANID |                       CAN data                        |
    |  ID0  |  D0  |  D1  |  D2  |  D3  |  D4  |  D5  |  D6  |  D7  |
```

values are in hex

```
            |                          byte                         |
    bits →  |  B0  |  B1  |  B2  |  B3  |  B4  |  B5  |  B6  |  B7  |
            |         high nibble       |         low nibble        |
```

values are in binary

## message id overview

| CAN ID          | Speed (ms) | Provides                                             | Model(s)       |
|-----------------|------------|------------------------------------------------------|----------------|
| [`120`](120.md) | 20         | Engine RPM, throttle, kill switch, throttle map      | 690 Enduro R   |
| [`121`](121.md) | 20         | Gears, clutch switch                                 | 690 Enduro R   |
| [`128`](128.md) | 20         |                                                      | 690 Enduro R   |
| [`129`](129.md) | 20         |                                                      | 690 Enduro R   |
| [`12A`](12A.md) | 50         | Throttle map (also)                                  | 690 Enduro R   |
| [`12B`](12B.md) | 10         | Front wheel speed, rear wheel speed, lean angle      | 690 Enduro R   |
| [`12C`](12C.md) | 100        | Rear wheel speed                                     | 690 Enduro R   |
| [`12E`](12E.md) | 20         |                                                      | 690 Enduro R   |
| [`174`](174.md) | 10         |                                                      | 690 Enduro R   |
| [`178`](178.md) | 10         |                                                      | 690 Enduro R   |
| [`17C`](17C.md) | 10         |                                                      | 690 Enduro R   |
| [`290`](290.md) | 10         | Front brake pressure                                 | 690 Enduro R   |
| [`450`](450.md) | 50         | Traction control                                     | 690 Enduro R   |
| [`540`](540.md) | 100        | Side stand switch, oil temp                          | 690 Enduro R   |
| [`541`](541.md) | 100        |                                                      | 690 Enduro R   |
| [`550`](550.md) | 50         | Kill switch (again), water temp                      | 690 Enduro R   |
| [`551`](551.md) |            | Fuel level                                           | SuperDuke 1290 |
| [`5A0`](5A0.md) | 100        |                                                      | 690 Enduro R   |
| [`7DF`](7DF.md) | varies     | OBD2 query                                           | 690 Enduro R   |
| [`7EA`](7EA.md) | varies     | OBD2 response                                        | 690 Enduro R   |
