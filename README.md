# A Simple USB to I2C Adapter

The I2C Adapter allows python programs to connect to I2C devices using an off the shelf Raspberry Pico board. The Raspberry Pico appears on the computer as a serial port (no device installation needed) and acts as a USB to I2C bridge. The Python package *i2c_adapter* provides an easy to use API to interact with the I2C devices that are connected to the I2C Adapter. 

 This adapter is used for example by the [GreenPak driver](https://pypi.org/project/greenpak) to program Renesas GreenPak SPLD devices.

<br>
<img  src="www/wiring_example.png"  
      style="display: block;margin-left: auto;margin-right: auto;width: 60%;" />
<br>

## Highlights

* Provides USB to I2C master functionality.
* Supports Windows/Mac/Linux.
* Uses a standard Raspberry Pico.
* Does not require driver installation (it appears on the computer as standard a serial port).
* Comes with an easy to use Python AP.
* Easy to modify/extend and to adapt to new hardware.

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

## Flashing the Raspberry Pico

**TL;DR**; Upload the file firmware.uf2 from the link below to the Raspberry Pico. It will now show up on your computer as a serial port and will act as a I2C Adapter.

### Step by step instructions

1. Download the file firmware.uf2 from here <https://github.com/zapta/i2c_adapter/tree/main/firmware/release>
1. **Press and hold the BOOTSEL button*** of the Raspberry Pico, connect it to a computer using a USB cable, and then release the button.
1. Confirm that the computer now has a new drive and that the Raspberry Pico LED is off.
1. Copy the firmware.uf2 file to that drive.
1. Confirm that the drive disappeared from your computer, and that the Raspberry Pico LED blinks shortly every 2 seconds.
1. Reconnect the Raspberry Pico again to the computer (without pressing its BOOTSEL button), and confirm that a new serial port appeared on your computer, and that the Raspberry Pico LED blinks shortly every 2 seconds.
1. Your Raspberry Pico is now a I2C Adapter and is ready to use.

<br>

## Connecting the Raspberry Pico

---
**IMPORTANT**

**The Raspberry Pico operates on 3.3V and is not 5V tolerant**. To connect to a 5V I2C device, use a bidirectional I2C level shifter such as <https://www.adafruit.com/product/5649#technical-details>.

---

| Signal         | Raspberry Pico Pin # | Description |
|--------------|:-----------:|------------|
| GND      | 3  |  Connect to the I2C device's GND.  This pin is nterchangeable with the other GND pins 8, 13, 18, 23, 28, 33, 38.   |
| SDA| 4      | Connect to the I2C device's SDA. If the I2C device doesn't have a pullup resistor, connect a pullup resistor between SDA and 3.3V.    | 
| SCL      | 5  | Connect to the I2C device's SCL. If the I2C device doesn't have a pullup resistor, connect a pullup resistor between SCL and 3.3V.       |
| 3.3V Supply     | 38  | Optional. May be used to power the I2C device.    |

<br>

## The wire protocol

See comments in [firmware source code](https://github.com/zapta/i2c_adapter/blob/main/firmware/platformio/src/main.cpp).

<bre>

## Firmware developement

1. Clone or download the repository to your computer.
2. Install [Visual Studio Code](https://code.visualstudio.com/)
3. In Visual Studio Code, install the plugin Platformio IDE.
4. In Visual Studio Code, use *Menu | File | Open Folder* open the firmware/platformio direcory in your local repository.
5. Wait until platformio will complete loading the necessary tools.
6. Edit the code in firmware/platformio/src directory.
7. Upload the modified firmware to your Raspberry Pico using the Platformio's Upload command (e.g use the '->' icon at the bottom).
