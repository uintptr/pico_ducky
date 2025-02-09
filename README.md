# Pico Ducky

A "rubber ducky" that runs on a Raspberry Pico W board (RP2040). Mainly using it
to wake up a laptop that doesn't support Wake-On-Lan (WOL) via HomeAssistant

## Wakeup the laptop

```
curl -v http://10.0.0.9:8080/api/wakeup
```

## Send arbitrary keystrokes via the `/api/type` REST API

using `test/req.json`
```
curl -v -X POST -H "Content-Type: application/json" -d "@test/req.json" http://10.0.0.9:8080/api/type
```

# Installation

## CircuitPython

https://circuitpython.org/

## Bundle files ( Extends CircuitPython )

https://github.com/adafruit/Adafruit_CircuitPython_Bundle

### Copy those directories under lib/ on the board

1. `adafruit_hid`
2. `adafruit_httpserver`

The root directory should look like this:

```
.
├── boot_out.txt
├── code.py
├── lib
│   ├── adafruit_hid
│   │   ├── consumer_control_code.mpy
│   │   ├── consumer_control.mpy
│   │   ├── __init__.mpy
│   │   ├── keyboard_layout_base.mpy
│   │   ├── keyboard_layout_us.mpy
│   │   ├── keyboard.mpy
│   │   ├── keycode.mpy
│   │   └── mouse.mpy
│   └── adafruit_httpserver
│       ├── authentication.mpy
│       ├── exceptions.mpy
│       ├── headers.mpy
│       ├── __init__.mpy
│       ├── interfaces.mpy
│       ├── methods.mpy
│       ├── mime_types.mpy
│       ├── request.mpy
│       ├── response.mpy
│       ├── route.mpy
│       ├── server.mpy
│       └── status.mpy
├── sd
│   └── placeholder.txt
├── settings.toml
└── wifi.json
```