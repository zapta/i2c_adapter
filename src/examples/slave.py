# A sample program that accepts handles serial_packets commands at endpoint 20.
# To test with master.py, use two serial points with crossed RX/TX.

from __future__ import annotations

# For using the local version of serial_packet.
import sys

# For using the local version of serial_packet. Comment out if
# using serial_packets package installed by pip.
sys.path.insert(0, "../../src")

import argparse
import asyncio
import logging
from typing import Tuple, Optional
from serial_packets.client import SerialPacketsClient
from serial_packets.packets import PacketStatus, PacketsEvent, PacketData

logging.basicConfig(level=logging.INFO,
                    format='%(relativeCreated)07d %(levelname)-7s %(filename)-10s: %(message)s')
logger = logging.getLogger("slave")

parser = argparse.ArgumentParser()
parser.add_argument("--port", dest="port", default=None, help="Serial port to use.")
args = parser.parse_args()


async def command_async_callback(endpoint: int, data: PacketData) -> Tuple[int, PacketData]:
    logger.info(f"Received command: [%d] %s", endpoint, data.hex_str())
    # Handle commands sent to end point 20.
    if (endpoint == 20):
        # Parse incoming command
        v1 = data.read_uint8()
        assert (v1 == 200)
        v2 = data.read_uint32()
        assert (v2 == 1234)
        assert (data.all_read_ok())
        # Return respose.
        status = PacketStatus.OK.value
        response_data = PacketData().add_uint16(3333).add_uint32(123456)
        logger.info(f"Command response: [%d] %s", status, response_data.hex_str())
        return (status, response_data)
    # Add here handling of additional endpoints.
    return (PacketStatus.UNHANDLED.value, bytearray())


async def message_async_callback(endpoint: int, data: PacketData) -> Tuple[int, PacketData]:
    logger.info(f"Received message: [%d] %s", endpoint, data.hex_str())


async def event_async_callback(event: PacketsEvent) -> None:
    logger.info("%s event", event)


async def async_main():
    logger.info("Started.")
    assert (args.port is not None)
    client = SerialPacketsClient(args.port, command_async_callback, message_async_callback,
                                 event_async_callback)
    while True:
        # Connect if needed.
        if not client.is_connected():
            if not await client.connect():
                await asyncio.sleep(2.0)
                continue
        # Here connected to port. Send a message every second.
        await asyncio.sleep(1)
        endpoint = 30
        data = PacketData().add_uint32(12345678)
        logger.info(f"Sending message: [%d] %s", endpoint, data.hex_str())
        client.send_message(endpoint, data)


asyncio.run(async_main(), debug=True)
