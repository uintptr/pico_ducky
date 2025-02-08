#!/usr/bin/env python3

import os
import sys
import usb_hid
import wifi
import socketpool
import board
import digitalio

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_httpserver import Server, Request, Response, Route

from adafruit_httpserver.status import *

LISTENING_PORT = 8080


def wifi_connect():

    hello = os.getenv("HELLO")
    print(hello)

    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    print(f"Connecting to {ssid}...")
    wifi.radio.connect(ssid, password)  # type: ignore
    print(f"Connected to {ssid}")


class KeyStroke:

    def __init__(self) -> None:
        self.kbd = Keyboard(usb_hid.devices)

    def api_wakeup(self, request: Request) -> Response:
        print("sending ESC")
        self.kbd.send(Keycode.ESCAPE)
        return Response(request, status=OK_200)


def main() -> int:

    status = 1

    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    try:

        wifi_connect()

        pool = socketpool.SocketPool(wifi.radio)

        server = Server(pool)  # type: ignore

        ks = KeyStroke()

        routes = [
            Route("/api/wakeup", "GET", ks.api_wakeup)
        ]

        server.add_routes(routes)

        try:
            led.value = True
            addr = str(wifi.radio.ipv4_address)
            port = LISTENING_PORT
            print(f"serving on {addr}:{port}")
            server.serve_forever(host=addr, port=port)
        finally:
            led.value = False

        status = 0

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)

    return status


if __name__ == '__main__':

    main_status = main()

    print(f"main() returned {main_status}")

    if 0 != main_status:
        sys.exit(main_status)
