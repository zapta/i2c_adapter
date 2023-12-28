#!python

from i2c_adapter import I2cAdapter
from luma.oled.device import sh1106
from pathlib import Path
from luma.core.render import canvas
from PIL import ImageFont
import time

# Relevant links
# https://luma-oled.readthedocs.io/en/latest/
# https://github.com/rm-hull/luma.core/blob/master/luma/core/interface/serial.py#L25
# https://github.com/rm-hull/luma.examples/tree/master/examples
# https://github.com/rm-hull/luma.examples/blob/master/examples/sys_info.py


class MyLumaSerial:
    """I2C implementation of the Luma 'Serial' interface."""
    def __init__(self, i2c: I2cAdapter, address: int):
        self._i2c: I2cAdapter = i2c
        self._addr = int(str(address), 0)
        assert 0 <= self._addr <= 127

    def command(self, *cmd):
        """Send command bytes."""
        assert len(cmd) <= 32
        payload = bytearray()
        payload.append(0x00)
        payload.extend(bytearray(list(cmd)))
        ok: bool = self._i2c.write(self._addr, payload)
        assert ok

    def data(self, data):
        """Send data bytes."""
        assert isinstance(data, bytearray)
        i = 0
        n = len(data)
        while i < n:
            chunk_size = min(256, n - i)
            assert chunk_size > 1
            payload = bytearray()
            payload.append(0x40)
            payload.extend(data[i : i + chunk_size])
            assert len(payload) == chunk_size + 1
            self._i2c.write(self._addr, payload)
            i += chunk_size


i2c = I2cAdapter(port="COM18")

# Scan the I2C bus. 
for adr in range(0, 127):
    if i2c.write(adr, bytearray([0]), silent=True):
        print(f"I2C response at 0x{adr:02x}")

# Create a Luma device.
my_luma_serial = MyLumaSerial(i2c, 0x2c)                             
device = sh1106(my_luma_serial, width=128, height=64, rotate = 0)

# Draw.
font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'C&C Red Alert [INET].ttf'))
font2 = ImageFont.truetype(font_path, 12)
with canvas(device) as draw:
    i = 0
    while True:
      draw.text((0, 0), str(i), font=font2, fill="white")
      i += 1
      time.sleep(0.5)
    
