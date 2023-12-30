#!python

from i2c_adapter import I2cAdapter
from luma.oled.device import sh1106
from luma.core.render import canvas
import time

# Resources
# https://buildmedia.readthedocs.org/media/pdf/luma-oled/rtd-update/luma-oled.pdf
# https://github.com/rm-hull/luma.core/blob/master/luma/core/interface/serial.py#L25
# https://github.com/rm-hull/luma.examples/blob/master/examples/sys_info.py
# https://github.com/rm-hull/luma.examples/tree/master/examples
# https://luma-oled.readthedocs.io/en/latest/


class MyLumaSerial:
    """Implementation of the Luma 'Serial' interface using the I2C Adapter"""

    def __init__(self, port: str, addr: int, cmd_mode: int, data_mode: int):
        self._i2c = I2cAdapter(port)
        self._addr = int(str(addr), 0)
        self._cmd_mode = cmd_mode
        self._data_mode = data_mode

    def command(self, *cmd):
        """Send command bytes."""
        cmd_bytes = bytearray(list(cmd))
        payload = bytearray()
        payload.append(self._cmd_mode)
        payload.extend(cmd_bytes)
        assert self._i2c.write(self._addr, payload)

    def data(self, data):
        """Send data bytes."""
        data = bytearray(data)
        i = 0
        n = len(data)
        while i < n:
            chunk_size = min(256, n - i)
            payload = bytearray()
            payload.append(self._data_mode)
            payload.extend(data[i : i + chunk_size])
            assert self._i2c.write(self._addr, payload)
            i += chunk_size


# Hint: use scan.py to find your oled's address.
luma_serial = MyLumaSerial("COM18", addr=0x3C, cmd_mode=0x00, data_mode=0x40)
oled = sh1106(luma_serial, width=128, height=64, rotate=0)

i = 0
while True:
    with canvas(oled) as draw:
        print(f"Drawing {i}", flush=True)
        draw.rectangle(oled.bounding_box, outline="white", fill="black")
        draw.text((19, 15), f"Hello  I2C Adapter", fill="white")
        draw.text((47, 42), f"{i:05d}", fill="white")
    i += 1
    time.sleep(1.0)
