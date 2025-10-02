"""Helper module for GPO support in AstralPool Halo Chlorinator.

This module extends the pychlorinator library with GPO-specific functionality.
"""
from __future__ import annotations

import asyncio
import logging
import struct
from enum import IntEnum

from bleak import BleakClient
from pychlorinator.halochlorinator import encrypt_characteristic
from pychlorinator.halochlorinator import encrypt_mac_key
from pychlorinator.halochlorinator import HaloChlorinatorAPI
from pychlorinator.halochlorinator import UUID_MASTER_AUTHENTICATION_2
from pychlorinator.halochlorinator import UUID_RX_CHARACTERISTIC
from pychlorinator.halochlorinator import UUID_SLAVE_SESSION_KEY_2

_LOGGER = logging.getLogger(__name__)


class GPOAppActions(IntEnum):
    """Actions that can be performed on GPO outputs."""

    NoAction = 0
    Off = 1
    Auto = 2
    On = 3


class GPOAction:
    """Represent a GPO action command."""

    def __init__(
        self,
        action: GPOAppActions = GPOAppActions.NoAction,
        gpo_number: int = 1,  # GPO1-GPO4
        header_bytes: bytes = b"\x03\xf8\x01",  # 504
    ) -> None:
        """Initialize GPO action.

        Args:
            action: The action to perform (Off, Auto, On)
            gpo_number: The GPO output number (1-4)
            header_bytes: The header bytes for the BLE command
        """
        self.action = action
        self.gpo_number = gpo_number
        self.header_bytes = header_bytes

    def __bytes__(self):
        """Convert to bytes for BLE transmission."""
        fmt = "=3s B B 15x"
        _LOGGER.info(
            "Selected GPO Action is %s for GPO%d", self.action, self.gpo_number
        )
        return struct.pack(fmt, self.header_bytes, self.action, self.gpo_number - 1)


async def async_write_gpo_action(
    chlorinator: HaloChlorinatorAPI, action: GPOAppActions, gpo_number: int
) -> None:
    """Connect to the Chlorinator and write a GPO action command to it.

    Args:
        chlorinator: The HaloChlorinatorAPI instance
        action: The GPO action to perform
        gpo_number: The GPO output number (1-4)

    Raises:
        ValueError: If gpo_number is not in range 1-4
        Exception: If BLE communication fails
    """
    if not 1 <= gpo_number <= 4:
        raise ValueError(f"GPO number must be between 1 and 4, got {gpo_number}")

    _LOGGER.info(
        "Writing GPO action: GPO%d -> %s", gpo_number, GPOAppActions(action).name
    )

    while chlorinator._connected:
        _LOGGER.debug("Already connected, Waiting")
        await asyncio.sleep(1)

    try:
        async with BleakClient(chlorinator._ble_device, timeout=10) as client:
            chlorinator._session_key = await client.read_gatt_char(
                UUID_SLAVE_SESSION_KEY_2
            )
            _LOGGER.debug("Got session key %s", chlorinator._session_key.hex())

            mac = encrypt_mac_key(
                chlorinator._session_key, bytes(chlorinator._access_code, "utf_8")
            )
            _LOGGER.debug("Mac key to write %s", mac)
            await client.write_gatt_char(UUID_MASTER_AUTHENTICATION_2, mac)

            data = GPOAction(action, gpo_number).__bytes__()
            _LOGGER.debug("Data to write %s", data.hex())
            data = encrypt_characteristic(data, chlorinator._session_key)
            _LOGGER.debug("Encrypted data to write %s", data.hex())
            await client.write_gatt_char(UUID_RX_CHARACTERISTIC, data)

            _LOGGER.info(
                "Successfully wrote GPO action for GPO%d: %s",
                gpo_number,
                GPOAppActions(action).name,
            )
    except Exception as e:
        _LOGGER.error("Failed to write GPO action for GPO%d: %s", gpo_number, str(e))
        raise


def add_gpo_support(chlorinator: HaloChlorinatorAPI) -> None:
    """Add GPO support methods to a HaloChlorinatorAPI instance.

    This function monkey-patches the chlorinator instance to add
    async_write_gpo_action method.

    Args:
        chlorinator: The HaloChlorinatorAPI instance to enhance
    """

    async def _async_write_gpo_action_wrapper(
        action: GPOAppActions, gpo_number: int
    ) -> None:
        """Wrapper method for async_write_gpo_action."""
        await async_write_gpo_action(chlorinator, action, gpo_number)

    # Add the method to the instance
    chlorinator.async_write_gpo_action = _async_write_gpo_action_wrapper
    _LOGGER.debug("Added GPO support to HaloChlorinatorAPI instance")
