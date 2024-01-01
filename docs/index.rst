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
The package is available from PyPi at https://pypi.org/project/i2c-adapter and can be installed
using pip:

.. code-block:: shell

  pip install i2c_adapter



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


API Reference
=============

.. toctree::
  :maxdepth: 2
  :caption: Contents:

.. automodule:: i2c_adapter
  :members:
  :member-order: bysource


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
