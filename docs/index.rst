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
| **Sparkfun Pro Micro RP2040** | Qwiic SDA | Qwiic SCL  | 2.2K     |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+
| **Adafruit KB2040**           | Qwiic SDA | Qwiic SCL  | No       |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+
| **Adafruit QT Py RP2040**     | Qwiic SDA | Qwiic SCL  | No       |  3.3V   |
+-------------------------------+-----------+------------+----------+---------+

|

API Installation
================

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

The Wire Protocol
=================

TBD

|

Firmware Development
=====================

The firmware is written in C++ and is developed as a platformio project under Visual Studio Code. The following
sections summarize the key aspect of the firmware development.

Project Structure
----------------------------
The platformio project resides in the firmware/platformio directory of the I2C Adapter repository https://github.com/zapta/i2c_adapter, 
the project configuration is in the `platformio.ini <https://github.com/zapta/i2c_adapter/tree/main/firmware/platformio>`_ file
and the source code is in the  `src directory <https://github.com/zapta/i2c_adapter/blob/main/firmware/platformio/src>`_.

Setting up the environment
--------------------------
1. Install Microsoft's Visual Studio Code ('VSC')
#. In VSC, add the extension 'platformio'
#. Clone the I2C Adapter `github repository <https://github.com/zapta/i2c_adapter>`_ on your computer.
#. Use VSC's 'file | open-folder', to open the 'platformio' directory in your local repository.
#. After platformio will complete installing the necessary tools, click on the 'build' icon in the status bar to verify that the project builds correctly.

Testing a new firmware version
------------------------------
1. Make the changes in the source code.
#. Connect a compatible board to your computer.
#. Select in the status bar the board target that matches your board.
#. Use the 'upload' button in the status bar to build and upload the binary to the board.

Generating new binaries
-----------------------
Run the python script 'build_env.py' and it will build binaries for all the targets and will copy them to 
release directory.

Adding a new board
------------------------------
Board definitions resides in platformio.ini and in src/board.cpp and the amount
of refactoring needed to add a board depends how close it is to the existing boards.
Adding a typical board includes adding:

* A new target to platformio.ini

* A new section in src/boards.cpp.

* A new row to the documentation's list.

* A new binary to the release.

.. toctree::
  :maxdepth: 2
  :caption: Contents:

