# A Simple USB to I2C Adapter

The I2C Adapter allows python programs to connect to I2C/QUIIC/STEMMA-QT devices using off the shelf low cost boards such the Raspberry Pico or SparkFun Pro Micro - RP2040. The I2C adapter appears on the computer as a serial port (no device installation required) and acts as a USB to I2C bridge, and this Python package  provides an easy to use API to interact with it using high level commands. 

 This adapter is used for example by the [GreenPak driver](https://pypi.org/project/greenpak) to program Renesas GreenPak SPLD devices.

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

i2c = i2c.I2cAdapter(port="COM7")
i2c_addr = 0x08
assert i2c.write(i2c_addr, bytearray([0]))
data = i2c.read(i2c_addr,  20)
print(data)
```

<br>

## LED Status

| I2C Adapter state         | Raspberry Pi LED state
|--------------|-----------|
| Idle, waiting for a command.  | A short blink every two seconds.
| Performing a command.  | On.
| Firmware flashing mode. | Off

<br>

## Connecting your I2C Adapter

---
**IMPORTANT**

**Do not to exceed the maximal voltage of your board. If needed,  use a bidirectional I2C level shifter such as <https://www.adafruit.com/product/5649#technical-details>.

---
Flash your board with the corresponding firmware from  <https://github.com/zapta/i2c_adapter/tree/main/firmware/release> and connect according to the table below:

| Board         | SDA |  SCL | Internal Pullups | Max Voltage |
|--------------|-----------|------------|:------------:|---|
| Raspberry Pico | GPIO4 | GPIO5 |  No|  3.3V |
| Sparkfun Pro Micro RP2040 | Qwicc SDA | Qwicc SCL | 2.2K |  3.3V|
| Adafruit KB2040 | Qwicc SDA | Qwicc SCL | No | 3.3V|
| Adafruit QT Py RP2040 | Qwicc SDA | Qwicc SCL | No | 3.3V |




<br>

## The wire protocol

See comments in the [firmware source code](https://github.com/zapta/i2c_adapter/blob/main/firmware/platformio/src/main.cpp).

<bre>

## For firmware developers

We use Visual Code Studion with the Platformio plug in to develope the firmware. Once you install both, clone this repository <https://github.com/zapta/i2c_adapter> on your machine and use the Menu | File | Open Folder option to open the firmware/platformio directory in the repository. Platformio take a few minutes do configure your environment and you will be able to edit/compile/upload code. Building firmware releases is done by running the Python script build_envs.py.





