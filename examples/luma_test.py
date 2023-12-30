#!python

from luma.oled.device import sh1106
from luma.core.render import canvas
import time


t0 = time.time()

def ts():
    return f"[{time.time() - t0:6.3f}]"

class MyDummySerial:
    def __init__(self):
        pass

    def command(self, *cmd):
        """Send command bytes."""
        cmd_bytes = bytearray(list(cmd))
        print(f"{ts()} CMD ({len(cmd_bytes)}): {cmd_bytes.hex(sep=' ')}", flush=True)

    def data(self, data):
        """Send data bytes."""
        data_bytes = bytearray(data)
        print(f"{ts()} DATA ({len(data_bytes)}): {data_bytes.hex(sep=' ')}", flush=True)


my_dummy_serial = MyDummySerial()
device = sh1106(my_dummy_serial, width=128, height=64, rotate=0)

with canvas(device) as c:
    for i in range(10):
        print(f"{ts()} Drawing {i}", flush=True)
        c.rectangle(device.bounding_box, outline="white", fill="black")
        c.text((30, 40), "Hello", fill="white")
        time.sleep(0.5)
