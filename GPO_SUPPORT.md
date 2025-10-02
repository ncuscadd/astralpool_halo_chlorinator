# GPO Support for AstralPool Halo Chlorinator

## Overview

This implementation adds full Home Assistant support for controlling GPO (General Purpose Output) outputs on the AstralPool Halo Chlorinator via BLE.

## Features

### Select Entities
- **GPO1-GPO4 Mode Select**: Control each GPO output with three options:
  - **Off**: Turn the GPO output off
  - **Auto**: Set the GPO to automatic mode (controlled by device schedules/logic)
  - **On**: Turn the GPO output on

### Sensors (Optional)
- **GPO1-GPO4 Mode Sensor**: Display the current mode of each GPO
- **GPO1-GPO4 State Sensor**: Display the current state (on/off) of each GPO

## Technical Details

### BLE Command Structure

The GPO control uses BLE characteristic 504 (0x1F8) with the following command structure:

```
Header: 0x03, 0xF8, 0x01 (3 bytes)
Action: GPOAppActions enum value (1 byte)
  - 0: NoAction
  - 1: Off
  - 2: Auto
  - 3: On
GPO Number: 0-3 (for GPO1-GPO4) (1 byte)
Padding: 15 bytes of zeros
```

### Implementation Components

1. **gpo_helper.py**: 
   - Defines `GPOAppActions` enum with action values
   - Defines `GPOAction` class for formatting BLE commands
   - Provides `async_write_gpo_action()` function for sending commands
   - Includes `add_gpo_support()` to monkey-patch the HaloChlorinatorAPI

2. **__init__.py**: 
   - Calls `add_gpo_support()` when initializing HCHLOR devices

3. **coordinator.py**: 
   - Detects GPO outlets that are enabled via `GPO{n}_OutletEnabled` or `GPO{n}_Mode` keys
   - Triggers dynamic entity creation for each enabled GPO

4. **select.py**: 
   - Implements `GPOModeSelect` entity for each GPO
   - Provides Off/Auto/On options
   - Handles state changes and calls the BLE write function

5. **sensor.py**: 
   - Dynamically creates sensor entities for GPO mode and state
   - Uses standard Home Assistant sensor patterns

## Usage

### Automatic Detection

The integration will automatically detect which GPO outputs are configured on your Halo device and create the corresponding entities. GPOs are detected when:
- The device reports `GPO{n}_OutletEnabled = 1` in the characteristics, OR
- The device reports a `GPO{n}_Mode` value

### Manual Control

1. Navigate to your HCHLOR device in Home Assistant
2. Find the GPO Mode Select entities (e.g., "GPO1 Mode")
3. Choose from:
   - **Off**: Manually turn off the output
   - **Auto**: Let the device control the output automatically
   - **On**: Manually turn on the output

### Automation Example

```yaml
automation:
  - alias: "Turn on GPO1 at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: select.select_option
        target:
          entity_id: select.hchlor_gpo1_mode
        data:
          option: "On"
```

## Troubleshooting

### Enable Debug Logging

Add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.astralpool_halo_chlorinator: debug
    custom_components.astralpool_halo_chlorinator.gpo_helper: debug
```

### Common Issues

1. **GPO entities not appearing**:
   - Ensure your Halo device has GPO outputs configured
   - Check the logs for `GPO{n}_OutletEnabled` or `GPO{n}_Mode` messages
   - Verify your device is within BLE range

2. **Commands not working**:
   - Check debug logs for BLE communication errors
   - Ensure no other app (e.g., mobile app) is connected to the device
   - Verify the GPO is properly wired and configured in the device

3. **State not updating**:
   - The state updates on the next polling cycle (20 seconds)
   - Check that the coordinator is successfully gathering data
   - Review logs for any BLE connection issues

## Protocol Notes

The GPO control protocol follows the same pattern as other Halo accessories:
- Uses the same authentication and encryption as other BLE commands
- Command characteristic: UUID_RX_CHARACTERISTIC
- Response is received via the standard polling mechanism
- State is read from EquipmentModeStateCharacteristicV2 (characteristic 206)

## Testing

When testing, look for these log messages:

```
INFO: Selected GPO Action is <action> for GPO<n>
DEBUG: Data to write <hex>
DEBUG: Encrypted data to write <hex>
INFO: Successfully wrote GPO action for GPO<n>: <action>
```

## Future Enhancements

Potential improvements:
- Support for Relay and Valve outputs (using similar patterns)
- GPO naming customization from device configuration
- Timer control for GPOs
- State binary sensors for on/off indication
