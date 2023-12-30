#!python

from i2c_adapter import I2cAdapter
from luma.oled.device import sh1106
from pathlib import Path
from luma.core.render import canvas
from PIL import ImageFont
import time
from typing import List

# Relevant links
# https://luma-oled.readthedocs.io/en/latest/
# https://github.com/rm-hull/luma.core/blob/master/luma/core/interface/serial.py#L25
# https://github.com/rm-hull/luma.examples/tree/master/examples
# https://github.com/rm-hull/luma.examples/blob/master/examples/sys_info.py
# https://buildmedia.readthedocs.org/media/pdf/luma-oled/rtd-update/luma-oled.pdf

# OLED display I2C address.
addr = 0x3c

class MyLumaSerial:
    """I2C implementation of the Luma 'Serial' interface."""
    def __init__(self, i2c: I2cAdapter, address: int):
        self._i2c: I2cAdapter = i2c
        self._addr = int(str(address), 0)
        assert 0 <= self._addr <= 127

    def command(self, *cmd):
        """Send command bytes."""
        assert isinstance(cmd, tuple)
        assert isinstance(cmd[0], int)
        assert len(cmd) <= 32
        cmd_bytes = bytearray(list(cmd))
        assert len(cmd_bytes) == len(cmd)
        print(f"cmd ({len(cmd_bytes)}): {cmd_bytes}", flush=True)
        payload = bytearray()
        payload.append(0x00)
        payload.extend(cmd_bytes)
        ok: bool = self._i2c.write(self._addr, payload)
        assert ok

    def data(self, data:List[int]):
        """Send data bytes."""
        assert isinstance(data, List)
        assert isinstance(data[0], int)
        print(f"data: {data} bytes", flush=True)
        data = bytearray(data)
        i = 0
        n = len(data)
        while i < n:
            chunk_size = min(256, n - i)
            assert chunk_size > 1
            payload = bytearray()
            payload.append(0x40)
            payload.extend(data[i : i + chunk_size])
            assert len(payload) == chunk_size + 1
            print(f"data chunk payload ({chunk_size}): {payload}", flush=True)
            self._i2c.write(self._addr, payload)
            i += chunk_size


i2c = I2cAdapter(port="COM18")

# Scan the I2C bus. 
# for adr in range(0, 127):
#     if i2c.write(adr, bytearray([0]), silent=True):
#         print(f"I2C response at 0x{adr:02x}")

# Create a Luma device.
my_luma_serial = MyLumaSerial(i2c, addr)                             
device = sh1106(my_luma_serial, width=128, height=64, rotate = 0)

# Draw.
with canvas(device) as c:
    i = 0
    while True:
      print(f"Drawing {i}", flush=True)
      c.rectangle(device.bounding_box, outline="white", fill="black")
      c.text((30, 40), "Hello", fill="white")
      i += 1
      time.sleep(1.0)
    
