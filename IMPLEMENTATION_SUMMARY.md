# GPO Implementation Summary

## Overview

This implementation adds full Home Assistant support for controlling GPO (General Purpose Output) outputs on the AstralPool Halo Chlorinator via BLE. The implementation has been completed and is ready for testing with a real device.

## Changes Made

### New Files Created

1. **`custom_components/astralpool_halo_chlorinator/gpo_helper.py`**
   - Defines `GPOAppActions` enum with action values (NoAction, Off, Auto, On)
   - Defines `GPOAction` class for formatting BLE commands
   - Implements `async_write_gpo_action()` function for sending GPO commands via BLE
   - Provides `add_gpo_support()` function to monkey-patch the HaloChlorinatorAPI

2. **`GPO_SUPPORT.md`**
   - Comprehensive documentation of GPO features
   - Usage examples and troubleshooting guide
   - BLE protocol details
   - Automation examples

3. **`test_gpo.py`**
   - Test script to verify GPO implementation
   - Demonstrates BLE command structure
   - Validates all GPO actions

### Modified Files

1. **`custom_components/astralpool_halo_chlorinator/__init__.py`**
   - Imports and applies GPO support to HaloChlorinatorAPI instances
   - No breaking changes to existing functionality

2. **`custom_components/astralpool_halo_chlorinator/coordinator.py`**
   - Detects GPO outlets via `GPO{n}_OutletEnabled` or `GPO{n}_Mode` keys
   - Triggers dynamic entity creation for each enabled GPO
   - Calls sensor and select callbacks for GPO entities

3. **`custom_components/astralpool_halo_chlorinator/select.py`**
   - Added `GPOModeSelect` class for each GPO (GPO1-GPO4)
   - Provides Off/Auto/On control options
   - Includes comprehensive error handling
   - Imports and uses GPOAppActions from gpo_helper

4. **`custom_components/astralpool_halo_chlorinator/sensor.py`**
   - Added `create_gpo_sensor_types()` function for dynamic GPO sensor creation
   - Creates sensors for GPO mode and state
   - Updates `add_sensor_callback` to support GPO sensors

5. **`README.md`**
   - Updated features table to include GPO control
   - Added link to GPO_SUPPORT.md documentation

## BLE Protocol Details

### Command Structure

The GPO control uses BLE characteristic 504 (0x1F8) with this structure:

```
Byte Offset | Content                           | Example (GPO2 Auto)
------------|-----------------------------------|--------------------
0-2         | Header (0x03, 0xF8, 0x01)         | 03 f8 01
3           | Action (1=Off, 2=Auto, 3=On)      | 02
4           | GPO Number (0-3 for GPO1-GPO4)    | 01
5-19        | Padding (15 bytes of zeros)       | 00 00 ... 00
```

### Verification

All GPO actions have been tested and produce correct BLE command bytes:

- GPO1 Off:  `03f8010100000000000000000000000000000000`
- GPO1 Auto: `03f8010200000000000000000000000000000000`
- GPO1 On:   `03f8010300000000000000000000000000000000`
- GPO2 Off:  `03f8010101000000000000000000000000000000`
- GPO2 Auto: `03f8010201000000000000000000000000000000`
- GPO2 On:   `03f8010301000000000000000000000000000000`
- (and so on for GPO3 and GPO4)

## Features Implemented

### Select Entities

For each enabled GPO (1-4), the integration creates:
- **Entity**: `select.hchlor_gpo{n}_mode`
- **Options**: Off, Auto, On
- **Icon**: mdi:power-plug
- **Device**: HCHLOR

### Sensors (Optional)

For each enabled GPO (1-4), the integration can create:
- **Mode Sensor**: `sensor.hchlor_gpo{n}_mode` - Shows current mode (Off/Auto/On)
- **State Sensor**: `sensor.hchlor_gpo{n}_state` - Shows current state (On/Off)

### Auto-Detection

The integration automatically detects which GPO outputs are configured on the device by checking for:
- `GPO{n}_OutletEnabled = 1` in the device data, OR
- Presence of `GPO{n}_Mode` value

## Code Quality

- ✅ All Python files pass `black` formatting
- ✅ All Python files pass `flake8` linting
- ✅ All Python files pass `reorder-python-imports`
- ✅ No syntax errors
- ✅ Follows existing code patterns in the repository
- ✅ Includes comprehensive error handling and logging
- ✅ Well-documented with docstrings

## Testing

### Unit Tests Completed

1. **Import Tests**: All modules import successfully
2. **Structure Tests**: GPOAction generates correct 20-byte commands
3. **Enum Tests**: GPOAppActions enum values are correct
4. **Protocol Tests**: All GPO/action combinations generate valid BLE commands

### Integration Testing Required

The following should be tested with a real Halo Chlorinator device:

1. **Entity Creation**
   - Verify GPO select entities appear in Home Assistant
   - Verify entities only appear for enabled GPO outputs
   - Verify entity names are correct (GPO1 Mode, GPO2 Mode, etc.)

2. **Control Testing**
   - Test setting GPO to Off
   - Test setting GPO to Auto
   - Test setting GPO to On
   - Verify device responds correctly to each command

3. **State Reporting**
   - Verify current GPO mode is displayed correctly
   - Verify state updates after mode change
   - Verify auto-refresh after command

4. **Error Handling**
   - Test behavior when BLE connection fails
   - Test behavior when device is busy
   - Verify error messages are logged correctly

## Debug Logging

To enable debug logging, add to Home Assistant's `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.astralpool_halo_chlorinator: debug
    custom_components.astralpool_halo_chlorinator.gpo_helper: debug
```

Expected log messages:
- `INFO: Writing GPO action: GPO{n} -> {action}`
- `DEBUG: Data to write {hex}`
- `DEBUG: Encrypted data to write {hex}`
- `INFO: Successfully wrote GPO action for GPO{n}: {action}`

## Usage Example

### Manual Control

1. Navigate to your HCHLOR device in Home Assistant
2. Find the GPO Mode Select entities (e.g., "GPO1 Mode")
3. Choose from Off, Auto, or On

### Automation Example

```yaml
automation:
  - alias: "Turn on pool pump (GPO1) at sunrise"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: select.select_option
        target:
          entity_id: select.hchlor_gpo1_mode
        data:
          option: "On"
```

## Backwards Compatibility

- ✅ No breaking changes to existing functionality
- ✅ Existing entities (chlorinator, heater, solar, lighting) remain unchanged
- ✅ GPO entities only appear when GPOs are detected on the device
- ✅ Works with pychlorinator v0.2.13 (current dependency version)

## Files for Review

All changes are in the branch: `copilot/fix-a224bc5d-59bf-47f0-a5fb-2e776feb0eba`

Key files to review:
1. `custom_components/astralpool_halo_chlorinator/gpo_helper.py` - New GPO support module
2. `custom_components/astralpool_halo_chlorinator/select.py` - GPOModeSelect entity
3. `custom_components/astralpool_halo_chlorinator/coordinator.py` - GPO detection logic
4. `GPO_SUPPORT.md` - User documentation
5. `test_gpo.py` - Test script

## Next Steps

1. **User Testing**: Test with a real Halo Chlorinator device that has GPO outputs configured
2. **Validation**: Verify BLE commands work correctly with the physical device
3. **Documentation**: Review and approve GPO_SUPPORT.md
4. **Release**: Merge to main branch and create a new release

## Notes

- The implementation uses characteristic 504 (0x1F8) for GPO commands, following the same pattern as other accessories (Heater: 502, Solar: 503, Lighting: 501)
- GPO outputs are auto-detected from the device's EquipmentModeStateCharacteristicV2 (characteristic 206)
- The implementation uses monkey-patching to add GPO support without modifying the pychlorinator library
- All code follows Home Assistant integration best practices
