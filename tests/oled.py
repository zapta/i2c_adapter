#!python

from i2c_adapter import I2cAdapter

i2c = I2cAdapter(port="COM18")
#i2c = I2cAdapter(port="COM17")

# Scan
for adr in range(0, 127):
  if i2c.write(adr, bytearray([0]), silent=True):
    print(f"I2C response at 0x{adr:02x}")


# i2c_addr = 0x08
# assert i2c.write(i2c_addr, bytearray([0]))
# data = i2c.read(i2c_addr, 20)
# print(data)
