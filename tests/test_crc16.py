# Unit tests of the CRC function

import unittest
import sys
from PyCRC.CRCCCITT import CRCCCITT

# Assuming VSCode project opened at repo directory
# sys.path.insert(0, "./src")
# from serial_packets.packets import PacketData


class TestCrc16(unittest.TestCase):
    # NOTE: According to https://srecord.sourceforge.net/crc16-ccitt.html#results
    # the correct value should be 0xE5CC and not 0x29B1.
    def test_data1(self):
        crc_gen = CRCCCITT("FFFF")
        data = bytearray([0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39])
        crc = crc_gen.calculate(bytes(data))
        # print(f"CRC:  {data} -> {crc:04x}\n", flush=True)
        self.assertEqual(crc, 0x29b1)

    def test_data2(self):
        crc_gen = CRCCCITT("FFFF")
        data = bytearray([0x01, 0x00, 0x00, 0x00, 0x07, 0x14, 0xc8, 0x00, 0x00, 0x04, 0xd2])
        crc = crc_gen.calculate(bytes(data))
        self.assertEqual(crc, 0x1f49)


if __name__ == '__main__':
    unittest.main()
