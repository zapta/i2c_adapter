.. I2C Adapter API documentation master file, created by
   sphinx-quickstart on Sun Dec 31 17:40:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. See rst cheat sheet at 
   https://docs.anaconda.com/restructuredtext/index.html

Overview
========

The I2C Adpater project allows to use off-the-shelf and inexpensive boards as USB to I2C bridge
by Mac, Windows, Linux and operating systems that supports portable Python. This document
describes the i2c_adapter portable Python package that provides the API to control the I2C Adapter.


|

.. image:: ../www/wiring_diagram.png
   :align: center

|

Examples
========

Write and read I2C device 0x08 with the I2C Adapter at serial port COM7:

.. code-block:: python
  :linenos:

  from i2c_adapter import I2cAdapter

  i2c = I2cAdapter(port="COM7")
  i2c_addr = 0x08
  assert i2c.write(i2c_addr, bytearray([0]))
  data = i2c.read(i2c_addr,  20)
  print(data)


Scan the I2C bus for devices:

.. code-block:: python
  :linenos:

  from i2c_adapter import I2cAdapter

  i2c = I2cAdapter(port="COM18")
  print(f"Scanning I2C bus 0x00 to 0x7f:")
  for adr in range(0, 127):
      if i2c.write(adr, bytearray([0]), silent=True):
          print(f"  - Found an I2C  device at 0x{adr:02x}")

|

Supported Boards
================

The able below lists the currently supported boards.
To make your own I2C Adapter, get one of these boards, and flash it according to the manufacturer's 
instructions with the corresponding I2C Adpter firmware from https://github.com/zapta/i2c_adapter/tree/main/firmware/release. 

:Example: 
  For the Raspberry Pico and similar RP2040 boards, flash it by connecting the board
  to your computer while holding the BOOTSEL button pressed to have the your computer recognize 
  the board as a disk driver, then copying the firmware file to that driver.

+-------------------------------+-----------+------------+----------+---------+
|                               | SDA       |  SCL       | Internal | Max     |
|                               |           |            | Pullups  | Voltage |
+===============================+===========+============+==========+=========+
| **Raspberry Pico**            | GP4       | GP5        |  No      |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+
| **Sparkfun Pro Micro RP2040** | Qwicc SDA | Qwicc SCL  | 2.2K     |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+
| **Adafruit KB2040**           | Qwicc SDA | Qwicc SCL  | No       |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+
| **Adafruit QT Py RP2040**     | Qwicc SDA | Qwicc SCL  | No       |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+

|

Installation
============

The Python API package is available from PyPi at https://pypi.org/project/i2c-adapter and can be installed
on your computer using pip:

.. code-block:: shell

  pip install i2c_adapter

:Note: 
  The I2C Adapter boards appear on the computer as a standard CDC serial port and
  thus do not require driver installation.

|

API Reference
=============

.. automodule:: i2c_adapter
  :members:
  :member-order: bysource

|

Wire Protocol
=============

TBD

|

Firmware Developement
=====================

TBD


.. toctree::
  :maxdepth: 2
  :caption: Contents:

