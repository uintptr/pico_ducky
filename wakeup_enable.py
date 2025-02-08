#!/usr/bin/env python3

import sys
import os
import glob


def find_product_root(name: str) -> str:

    for product in glob.glob("/sys/bus/usb/devices/*/product"):
        with open(product) as f:
            data = f.read().strip("\r\n")

        if name == data:
            return os.path.dirname(product)

    raise FileNotFoundError(f"Unable to find product={name}")


def enable_wakeup(product_root: str) -> None:

    wakeup_file = os.path.join(product_root, "power", "wakeup")

    with open(wakeup_file, "w+") as f:
        f.write("enabled")


def main() -> int:

    status = 1

    try:
        assert 0 == os.getuid(), "must be running as root"

        product_root = find_product_root("Pico W")

        enable_wakeup(product_root)

        status = 0

    except FileNotFoundError as e:
        print(e)
    except AssertionError as e:
        print(e)
    except KeyboardInterrupt:
        pass

    return status


if __name__ == '__main__':

    status = main()

    if 0 != status:
        sys.exit(status)
