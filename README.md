# Simple I2C Adapter
A simple USB to I2C adapter that uses Raspberry Pico board and provies an easy to use Python API.

Status: Fully functional and is used by the [GreenPak driver](https://pypi.org/project/greenpak).

Design goals:
* Provides USB to I2C master functionality.
* Supports Windows/Mac/Linux.
* Uses of-the-shelf inexpensive hardware (Raspberry Pico).
* No driver installation required (emulates a serial port).
* Provides an easy to use Pyton API.
* Can be easyly modified or adapted to new hardware.

example:

```python
from i2c_adapter import I2cAdapter

i2c = i2c.I2cAdapter(port="COM7")
device = 0x08
assert i2c.write(device, bytearray([0]))
data = i2c.read(device,  20)
print(data)
```
