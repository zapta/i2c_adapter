from typing import Optional, List, Tuple
from serial import Serial
import time


class I2cPicoDriver:
    def __init__(self, port: str):
        self.__serial: Serial = Serial(port, timeout=1.0)
        if not self.test_connection_to_driver():
            raise RuntimeError(f"i2c driver not detected at port {port}")

    def test_connection_to_driver(self, max_tries: int = 3) -> bool:
        """Use the ECHO command to test if the driver is connected to the host.
        This does not test the connection between the driver and the I2C device.
        Return True is the driver is responsive.
        """
        assert max_tries > 0
        for i in range(max_tries):
            if i > 0:
                # Delay to let any pending command to timeout.
                time.sleep(0.3)
            ok: bool = True
            for b in [0x00, 0xFF, 0x5A, 0xA5]:
                if not self.__test_echo_cmd(b):
                    ok = False
                    break
            if ok:
                # We had one good pass on all patterns. We are good.
                return True
        # All tries failed.
        return False

    def __test_echo_cmd(self, b: int) -> bool:
        """Test if an echo command with given byte returns the same byte. Used
        to test the connection to the driver."""
        assert isinstance(b, int)
        assert 0 <= b <= 256
        req = bytearray()
        # print(f"Type: {type(ord("e"))}")
        req.append(ord("e"))
        req.append(b)
        self.__serial.write(req)
        resp = self.__serial.read(1)
        assert isinstance(resp, bytes), type(resp)
        assert len(resp) == 1
        return resp[0] == b
      
    def i2c_reset(self) -> bool:
        """Reset the I2C interface. used to clear pending errors."""
        # assert isinstance(b, int)
        # assert 0 <= b <= 256
        req = bytearray()
        # print(f"Type: {type(ord("e"))}")
        req.append(ord("t"))
        # payload.append(b)
        # print(f"Reset payload: {payload.hex(sep=" ")}")
        self.__serial.write(req)
        resp = self.__serial.read(1)
        assert isinstance(resp, bytes), type(resp)
        assert len(resp) == 1
        # print(f"Reset resp: {resp.hex(sep=" ")}")
        return resp[0] == ord("K")

    def i2c_write(self, device_address: int, data: bytearray) -> bool:
        """Write data to the I2C device, return True if ok."""
        assert isinstance(device_address, int)
        assert 0 <= device_address <= 127
        assert isinstance(data, bytearray)
        assert 0 < len(data) <= 256

        # Construct and send the command.
        req = bytearray()
        req.append(ord("w"))
        req.append(device_address)
        req.append(len(data) // 256)
        req.append(len(data) % 256)
        req.extend(data)
        n = self.__serial.write(req)
        # print(f"write: payload {payload.hex(sep=" ")}", flush=True)
        if n != len(req):
            print(f"I2C write: write mismatch, expected {len(req)}, got {n}")
            return False

        # Read the status flag.
        resp = self.__serial.read(1)
        # print(f"write: resp1: {resp.hex(sep=" ")}")
        assert isinstance(data, bytearray), type(data)
        if len(resp) != 1:
            print(f"I2C write: status read mismatch, expected {1}, got {len(resp)}")
            return False
        if resp[0] not in (ord("E"), ord("K")):
            print(f"I2C write: unexpected status in response: {resp}")
            return False
        if resp[0] == ord("K"):
            return True

        # Read the extra info status byte.
        resp = self.__serial.read(1)
        assert isinstance(data, bytearray), type(data)
        # print(f"write: resp2: {resp.hex(sep=" ")}")
        if len(resp) != 1:
            print(
                f"I2C write: extra status read mismatch, expected {1}, got {len(resp)}"
            )
            return False
        # if not workaround:
        print(f"I2C write: failed with status = {resp[0]:02x}")
        return False

    def i2c_read(self, device_address: int, byte_count: int) -> Optional[bytearray]:
        """Read a given number of bytes from the device. Returns the bytes or None if error."""
        assert isinstance(device_address, int)
        assert 0 <= device_address <= 127
        assert isinstance(byte_count, int)
        assert 0 < byte_count <= 256

        # Construct and send the command
        req = bytearray()
        req.append(ord("r"))
        req.append(device_address)
        req.append(byte_count // 256)
        req.append(byte_count % 256)
        n = self.__serial.write(req)
        if n != len(req):
            print(f"I2C read: write mismatch, expected {len(req)}, got {n}")
            return None

        # Read status flag.
        resp = self.__serial.read(1)
        assert isinstance(resp, bytes), type(resp)
        if len(resp) != 1:
            print(f"I2C read: status flag read mismatch, expected {1}, got {len(resp)}")
            return None
        status_flag = resp[0]
        if status_flag not in (ord("E"), ord("K")):
            print(f"I2C read: unexpected status flag in response: {resp}")
            return None

        # Handle the error case.
        if status_flag == ord("E"):
            resp = self.__serial.read(1)
            assert isinstance(resp, bytes), type(resp)
            if len(resp) != 1:
                print(
                    f"I2C read: error info read mismatch, expected {1}, got {len(resp)}"
                )
                return None
            print(f"I2C read: failed with status = {resp[1]:02x}")
            return None

        # Here we are in the OK case. First read the count.
        resp = self.__serial.read(2)
        assert isinstance(resp, bytes), type(resp)
        if len(resp) != 2:
            print(f"I2C read: error count read mismatch, expected {2}, got {len(resp)}")
            return None
        resp_count = (resp[0] << 8) + resp[1]
        if resp_count != byte_count:
            print(
                f"I2C read: response count mismatch, expected {byte_count}, got {resp_count}"
            )
            return None

        # Now read the data
        resp = self.__serial.read(byte_count)
        assert isinstance(resp, bytes), type(resp)
        if len(resp) != byte_count:
            print(
                f"I2C read: data read mismatch, expected {byte_count}, got {len(resp)}"
            )
            return None
        return bytearray(resp)
