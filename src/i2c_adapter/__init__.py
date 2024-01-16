"""The ``i2c_adapter`` package provides the API to access I2C Adapter boards. To access an I2C Adapter,
create an object of the  class I2CAdapter, and use the methods it provides.
"""

from typing import Optional, List, Tuple
from serial import Serial
import time


# NOTE: Numeric values match wire protocol.
class AuxPinMode(Enum):
    """Auxilary pin modes."""

    INPUT_PULLDOWN = 1
    INPUT_PULLUP = 2
    OUTPUT = 3


class I2cAdapter:
    """Connects to the I2C Adapter at the specified serial port and asserts that the
    I2C responses as expcted.

    :param port: The serial port of the I2C Adapter. I2C Adapters
        appear on the local computer as a standard serial port
    :type port: str
    """

    def __init__(self, port: str):
        self.__serial: Serial = Serial(port, timeout=1.0)
        if not self.test_connection_to_driver():
            raise RuntimeError(f"i2c driver not detected at port {port}")
        adapter_info = self.__read_adapter_info()
        if adapter_info is None:
            raise RuntimeError(f"i2c driver failed to read adapter info at {port}")
        print(f"Adapter info: {adapter_info.hex(" ")}", flush=True)
        if adapter_info[0] != 0x45 or adapter_info[1] != 0x67 or adapter_info[2] != 0x3:
            raise RuntimeError(f"Unexpected I2C adapter info at {port}")

    def __read_adapter_response(
        self, op_name: str, ok_resp_size: int, silent: bool
    ) -> bytes:
        """A common method to read a response from the adapter.
        Returns None if error, otherwise OK response bytes"""
        assert isinstance(op_name, str)
        assert isinstance(ok_resp_size, int)
        assert 0 <= ok_resp_size
        # Read status flag.
        ok_resp = self.__serial.read(1)
        assert isinstance(ok_resp, bytes), type(ok_resp)
        if len(ok_resp) != 1:
            print(
                f"{op_name}: status flag read mismatch, expected {1}, got {len(ok_resp)}",
                flush=True,
            )
            return None
        status_flag = ok_resp[0]
        if status_flag not in (ord("E"), ord("K")):
            print(
                f"{op_name}: unexpected status flag in response: {ok_resp}", flush=True
            )
            return None

        # Handle the case of an error
        if status_flag == ord("E"):
            # Read the additional error code byte.
            ok_resp = self.__serial.read(1)
            assert isinstance(ok_resp, bytes), type(ok_resp)
            if len(ok_resp) != 1:
                print(
                    f"{op_name}: error info read mismatch, expected {1}, got {len(ok_resp)}",
                    flush=True,
                )
                return None
            if not silent:
                print(f"{op_name}: failed with error code {ok_resp[0]}", flush=True)
            return None

        # Handle the OK case.
        #
        # Read the expected byte data count.
        ok_resp = self.__serial.read(ok_resp_size)
        assert isinstance(ok_resp, bytes), type(ok_resp)
        if len(ok_resp) != ok_resp_size:
            print(
                f"{op_name}: OK resp read count mismatch, expected {ok_resp_size}, got {len(ok_resp)}",
                flush=True,
            )
            return None
        return ok_resp

    def read(
        self, device_address: int, byte_count: int, silent=False
    ) -> Optional[bytearray]:
        """Reads N bytes from an I2C device.

        :param device_address: I2C device address in the range [0, 0xff].
        :type device_address: int

        :param byte_count: The number of bytes to read. Should be in the range [0, 256].
        :type byte_count: int

        :param silent: If true, supress printing of error messages. Useful when using the method
            to scan the I2C bus for devices. Default value is good for most other use cases
        :type silent: bool

        :returns: A bytearray with ``byte_count`` bytes read, or None if an error
        :rtype: bytearray
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
            print(f"I2C read: write mismatch, expected {len(req)}, got {n}", flush=True)
            return None

        ok_resp = self.__read_adapter_response(
            "I2C read", ok_resp_size=2, silent=silent
        )
        if ok_resp is None:
            return None

        resp_count = (ok_resp[0] << 8) + ok_resp[1]
        if resp_count != byte_count:
            print(
                f"I2C read: response count mismatch, expected {byte_count}, got {resp_count}",
                flush=True,
            )
            return None

        # Read the data bytes
        resp = self.__serial.read(byte_count)
        assert isinstance(resp, bytes), type(resp)
        if len(resp) != byte_count:
            print(
                f"I2C read: data read mismatch, expected {byte_count}, got {len(resp)}",
                flush=True,
            )
            return None
        return bytearray(resp)

    def write(self, device_address: int, data: bytearray | bytes, silent=False) -> bool:
        """Write N bytes to an I2C device.

        :param device_address: I2C device address in the range [0, 0xff].
        :type device_address: int

        :param data: The bytes to write. ``len(data)`` should be in the range [0, 256].
        :type data: bytearray or bytes.

        :param silent: If true, supress printing of error messages. Useful when using the method
            to scan the I2C bus for devices. Default value is good for most other use cases.
        :type silent: bool

        :returns: True if ok, False if an error.
        :rtrype: bool
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
            print(
                f"I2C write: write mismatch, expected {len(req)}, got {n}", flush=True
            )
            return False

        # Read the response.
        ok_resp = self.__read_adapter_response(
            "I2C write", ok_resp_size=0, silent=silent
        )
        if ok_resp is None:
            return None

        # All ok.
        return True

    def set_aux_pin_mode(self, pin: int, pin_mode: AuxPinMode) -> bool:
        """Sets the mode of an auxilary pin.

        :param pin: The aux pin index, should be in [0, 7].
        :type pin: int

        :param pin_mode: The new pin mode.
        :type pin_mode: AuxPinMode

        :returns: True if OK, False otherwise.
        :rtype: bool
        """
        assert isinstance(pin, int)
        assert 0 <= pin <= 7
        assert isinstance(pin_mode, AuxPinMode)
        req = bytearray()
        req.append(ord("m"))
        req.append(pin)
        req.append(pin_mode.value)
        self.__serial.write(req)
        ok_resp = self.__read_adapter_response("Aux mode", 0)
        if ok_resp is None:
            return False
        return True

    def read_aux_pins(self) -> int | None:
        """Reads the auxilary pins.

        :returns: The pins value as a 8 bit in value or None if an error.
        :rtype: int | None
        """
        req = bytearray()
        req.append(ord("a"))
        self.__serial.write(req)
        ok_resp = self.__read_adapter_response("Aux read", 1)
        if ok_resp is None:
            return None
        return ok_resp[0]

    def write_aux_pins(self, values, mask=0b11111111) -> bool:
        """Writes the aux pins.

        :param values: An 8 bits integer with the bit values to write. In the range [0, 255].
        :type pin: int

        :param mask: An 8 bits int with mask that indicates which auxilary pins should be written. If
            the corresponding bits is 1 than the pin is updated otherwise it's left as is.
        :type mask: int

        :returns: True if OK, False otherwise.
        :rtype: bool
        """
        assert isinstance(values, int)
        assert 0 <= values <= 255
        assert isinstance(mask, int)
        assert 0 <= mask <= 255
        req = bytearray()
        req.append(ord("b"))
        req.append(values)
        req.append(mask)
        self.__serial.write(req)
        ok_resp = self.__read_adapter_response("Aux write", 0)
        if ok_resp is None:
            return False
        return True

    def test_connection_to_driver(self, max_tries: int = 3) -> bool:
        """Tests connection to the I2C Adapter.

        The method tests if the I2C adapter exists and is responding. It is provided
        for diagnostic purposes and is not needed in typical applications.

        :param max_tries: Max number of attempts. The default should be good for most case.
        :type max_tries: int

        :returns: True if connection is OK, false otherwise.
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
        """Test if an echo command with given byte returns the same byte. Used
        to test the connection to the driver."""
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

    def __read_adapter_info(self) -> Optional[bytearray]:
        """Return adapter info or None if an error."""
        req = bytearray()
        req.append(ord("i"))
        n = self.__serial.write(req)
        if n != len(req):
            print(f"I2C info: write mismatch, expected {len(req)}, got {n}", flush=True)
            return None
        ok_resp = self.__read_adapter_response("I2C adapter info", ok_resp_size=6, silent=False)
        return ok_resp
