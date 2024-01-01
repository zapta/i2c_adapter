.. I2C Adapter API documentation master file, created by
   sphinx-quickstart on Sun Dec 31 17:40:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Example
=======
Write and read I2C device 0x08 using the I2C Adapter at serial port COM7: 

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
      print(f"  - Device at 0x{adr:02x}")


API Reference
=============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. automodule:: i2cdriver
   :members:

.. automodule:: i2c_adapter
   :members:

.. autoclass:: i2c_adapter.I2cAdapter
   :member-order: bysource
   :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
