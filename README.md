# A Simple USB to I2C Adapter

The I2C Adapter allows python programs to connect to I2C/QUIIC/STEMMA-QT devices using off the shelf low cost boards such the Raspberry Pico or SparkFun Pro Micro - RP2040. The I2C adapter appears on the computer as a serial port (no device installation required) and acts as a USB to I2C bridge, and this Python package  provides an easy to use API to interact with it using high level commands. 

 This adapter is used for example by the [GreenPak driver](https://pypi.org/project/greenpak) to program Renesas GreenPak SPLD devices.

<br>
<img  src="www/wiring_diagram.png"
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

## Flashing a RP2040 board.

**TL;DR**; Use the BOOTSEL button flash your board with the corresponding .uf2 file from <https://github.com/zapta/i2c_adapter/tree/main/firmware/release>.

### Step by step instructions

1. Download the file .uf2 that corresponds to your board   <https://github.com/zapta/i2c_adapter/tree/main/firmware/release>
1. **Press and hold the BOOTSEL button*** of the board, connect it to a computer using a USB cable, and then release the button.
1. Confirm that the computer now has a new drive and that the Raspberry Pico LED is off.
1. Copy the the .uf2 file you download to that drive.
1. Confirm that the drive disappeared from your computer, and that the board's  LED blinks shortly every 2 seconds.
1. Reconnect the board again to the computer (without pressing its BOOTSEL button), confirm that a new serial port appeared on your computer, and that the board's LED blinks shortly every 2 seconds.
1. Your board is now a I2C Adapter and is ready to use.

<br>

## Connecting your board

---
**IMPORTANT**

**Do not to exceed the I2C signals levels of your board.** For example, if your board can handle only 3.3V signals and you want to connect it to a 5V I2C device, you need to use a bidirectional I2C level shifter such as <https://www.adafruit.com/product/5649#technical-details>.

---

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





