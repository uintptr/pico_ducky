#!/usr/bin/env python3

import os
import sys
import time

import usb_hid
import wifi
import socketpool
import board
import digitalio

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_httpserver import Server, Request, Response, Route


from adafruit_httpserver.status import *

LISTENING_PORT = 8080


def wifi_connect():

    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    print(f"Connecting to {ssid}...")
    wifi.radio.connect(ssid, password)  # type: ignore
    print(f"Connected to {ssid}")


def build_keycode_strings() -> dict[str, int]:

    keys: dict[str, int] = {}
    code = Keycode()

    for attr in dir(code):
        if attr.startswith("_"):
            continue
        if False == attr[0].isupper():
            continue

        keys[attr] = int(getattr(code, attr))

    return keys


class KeyStroke:

    def __init__(self) -> None:
        self.kbd = Keyboard(usb_hid.devices)
        self.layout = KeyboardLayoutUS(self.kbd)
        self.keycode_table = build_keycode_strings()

    def __command_handler(self, cmd: dict[str, str]) -> None:
        if "sleep" in cmd:
            time.sleep(int(cmd["sleep"]))
        elif "write" in cmd:
            self.layout.write(cmd["write"])
        elif "keycodes" in cmd:
            codes = cmd["keycodes"].split(",")
            if 1 == len(codes):
                assert codes[0] in self.keycode_table
                self.kbd.send(self.keycode_table[codes[0]])
            elif 2 == len(codes):
                assert codes[0] in self.keycode_table
                assert codes[1] in self.keycode_table
                self.kbd.press(self.keycode_table[codes[0]])
                self.kbd.send(self.keycode_table[codes[1]])
                self.kbd.release()
            else:
                count = len(codes)
                raise ValueError(f"Too many keycodes ({count})")

    def api_wakeup(self, request: Request) -> Response:
        print("sending ESC")
        self.kbd.send(Keycode.ESCAPE)
        return Response(request, status=OK_200)

    def api_type(self, request: Request) -> Response:

        data: dict[str, list] | None = request.json()  # type: ignore

        if data is None or "commands" not in data:
            return Response(request, status=BAD_REQUEST_400)

        commands: list[dict[str, str]] = data["commands"]

        try:
            for c in commands:
                self.__command_handler(c)

            return Response(request, status=OK_200)
        except AssertionError as e:
            err_msg = f"assertion: {e}"
        except ValueError as e:
            err_msg = f"value error: {e}"
        except Exception as e:
            err_msg = f"giant exception: {e}"

        return Response(request, body=err_msg, status=OK_200)


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
            Route("/api/wakeup", "GET", ks.api_wakeup),
            Route("/api/type", "POST", ks.api_type)
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
