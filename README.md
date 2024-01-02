# A Simple USB to I2C Adapter

The I2C Adapter allows python programs to connect to I2C/QUIIC/STEMMA-QT devices using off the shelf low cost boards such the Raspberry Pico or SparkFun Pro Micro - RP2040. The I2C adapter appears on the computer as a serial port (no device installation required) and acts as a USB to I2C bridge, and this Python package  provides an easy to use API to interact with it using high level commands. 


For example, the schematic below shows the wiring for the [oled_demo.py](https://github.com/zapta/i2c_adapter/blob/main/examples/oled_demo.py) example which drive an I2C OLED display using an I2C Adapter and the luma.oled python package.

<br>
<img  src="https://raw.githubusercontent.com/zapta/i2c_adapter/main/www/wiring_diagram.png"
      style="display: block;margin-left: auto;margin-right: auto;width: 80%;" />
<br>



## Highlights

* Provides USB to I2C-master bridge.
* Supports Windows/Mac/Linux.
* Uses low cost low cost off-the-shelf boards as adapters.
* Does not require driver installation (it appears on the computer as standard a serial port).
* Comes with an easy to use Python API.
* Easy to modify/extend and to adapt to new hardware.
* Permissive open source license. Comercial use OK, sharing and attribution not required. 

<br>

## Python API Example

Package installation

```bash
pip install i2c-adapter --upgrade
```

In the example below, we use an I2C Adapter that appears as serial port "COM7" to access an I2C device at address 0x08. First we write a single byte 0x00 and then read 20 bytes. Upon completion, the 'data' variable contains a bytearray with 20 bytes.

```python
from i2c_adapter import I2cAdapter

i2c = I2cAdapter(port="COM7")
i2c_addr = 0x08
assert i2c.write(i2c_addr, bytearray([0]))
data = i2c.read(i2c_addr,  20)
print(data)
```

In the example below we scan the I2C bus address range 0x00 to 0x7f and look for devices that response to an empty write.
```python
from i2c_adapter import I2cAdapter

i2c = I2cAdapter(port="COM18")
print(f"Scanning I2C bus 0x00 to 0x7f:")
for adr in range(0, 127):
    if i2c.write(adr, bytearray([0]), silent=True):
      print(f"  - Device at 0x{adr:02x}")
```

<br>

## Documentation

Full documentation is available at <https://i2c-adapter.readthedocs.io/>