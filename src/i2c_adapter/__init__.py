"""The i2c_adapter provides a an easy to use Python API for accessing I2C
 devices using an I2C Adapter compatible board."""

from typing import Optional, List, Tuple
from serial import Serial
import time


class I2cAdapter:
    """This class provides the Python API of the I2C Adapter."""

    def __init__(self, port: str):
        """Connect to the I2C Adapter board.

        Initializes this instance and tries to connect to an I2C Adapter
        at the specified serial port. The constructor asserts that the I2C
        Adapter was indeed found.

        :param port: The serial port of the I2C Adapter to connect. The format of
                the port string is operating system dependent and may look like "COM7" on
                windows, "/dev/tty.usbmodem1101" on Mac, and  "/dev/ttyUSB0" on Linux. If
        :type port: str
        """
        self.__serial: Serial = Serial(port, timeout=1.0)
        if not self.test_connection():
            raise RuntimeError(f"i2c driver not detected at port {port}")

    def read(
        self, device_address: int, byte_count: int, silent=False
    ) -> Optional[bytearray]:
        """Read N bytes from an I2C device.

        Performs an I2C start/read/stop transaction with the specified device.

        :param device_address: The I2C address of the device to read from. This
            value must be in the range [0, 0x7f]
        :type device_address: int

        :param byte_count: The number of bytes to read, must be in the range
            [0, 256]. If the count is 0, the adapter still performs a read
            transaction but reads zero bytes. This is useful when scanning the
            I2C bus for devices
        :type byte_count: int

        :param silent: If true, supresses error messages regarding communication error
            with the I2C device. This is useful for I2C bus scanning since most of
            the scanned addresses do not have a corresponding device.
        :type silent: bool

        :return: A bytearray with the bytes read if the operation was successful, otherwise
            None to indicate an error. The length of the bytearray is guaranteed to
            be equal to byte_count.
        :rtype: bytearray or None
        """
        assert isinstance(device_address, int)
        assert 0 <= device_address <= 127
        assert isinstance(byte_count, int)
        assert 0 <= byte_count <= 256

        # Construct and send the command request.
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

        # Handle the case of an error
        if status_flag == ord("E"):
            # Read the additional error info byte.
            resp = self.__serial.read(1)
            assert isinstance(resp, bytes), type(resp)
            if len(resp) != 1:
                print(
                    f"I2C read: error info read mismatch, expected {1}, got {len(resp)}"
                )
                return None
            if not slient:
                print(f"I2C read: failed with status = {resp[1]:02x}")
            return None

        # Handle the OK case.
        #
        # Read the returned data count.
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

        # Read the data bytes
        resp = self.__serial.read(byte_count)
        assert isinstance(resp, bytes), type(resp)
        if len(resp) != byte_count:
            print(
                f"I2C read: data read mismatch, expected {byte_count}, got {len(resp)}"
            )
            return None
        return bytearray(resp)

    def write(self, device_address: int, data: bytearray | bytes, silent=False) -> bool:
        """Write N bytes to an I2C device.

        Performs an I2C start/write/stop transaction with the specified device.

        :param device_address: The I2C address of the device to write to. This
            value must be in the range [0, 0x7f]
        :type device_address: int

        :param data: The bytes to write. len(data) must be in the range [0, 256]. If data is 
            emptry the transaction include the start/stop steps without byte writing. 
            This is useful when scanning the I2C bus for devices
        :type data: bytearray or bytess

        :param silent: If true, supresses error messages regarding communication error
            with the I2C device. This is useful for I2C bus scanning since most of
            the scanned addresses do not have a corresponding device.
        :type silent: bool

        :return: True operation was successful, False, otherwise.
        :rtype: bool
        """
        assert isinstance(device_address, int)
        assert 0 <= device_address <= 127
        assert isinstance(data, bytearray) or isinstance(data, bytes)
        assert 0 <= len(data) <= 256

        # Construct and send the command request.
        req = bytearray()
        req.append(ord("w"))
        req.append(device_address)
        req.append(len(data) // 256)  # Count MSB
        req.append(len(data) % 256)  # Count LSB
        req.extend(data)
        n = self.__serial.write(req)
        if n != len(req):
            print(f"I2C write: write mismatch, expected {len(req)}, got {n}")
            return False

        # Read the status flag.
        resp = self.__serial.read(1)
        assert isinstance(resp, bytes), type(resp)
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
        if len(resp) != 1:
            print(
                f"I2C write: extra status read mismatch, expected {1}, got {len(resp)}"
            )
            return False
        if not silent:
            print(f"I2C write: failed with status = {resp[0]:02x}")
        return False

    def test_connection(self, max_tries: int = 3) -> bool:
        """Tests the serial communication with the I2C Adapter.

        Tests the communication with the I2C Adapter by sending commands and verifying
        the returns response. This method doesn't invloved the I2C bus, not should it affect
        the I2C devices

        This methos is exposes for diagnostic purposes and is not necessary in typicall
        usage. It is used internally when the client API connects to the I2C adapter to
        confirm the connection

        
        :param max_tries: The maximum number of communication attempts to perform. In some
                cases more than one attempts may be needed for the I2C adapter and the API
                client to sync states. It's recomanded to not specify this argument and
                use the defaul value
        :type max_tries: int

        :return: True if test was successful, False otherwise
        :rtype: bool
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
        """Test if an echo command with given byte returns the exact same byte."""
        assert isinstance(b, int)
        assert 0 <= b <= 256
        req = bytearray()
        req.append(ord("e"))
        req.append(b)
        self.__serial.write(req)
        resp = self.__serial.read(1)
        assert isinstance(resp, bytes), type(resp)
        assert len(resp) == 1
        return resp[0] == b
