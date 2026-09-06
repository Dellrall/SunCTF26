---
description: Hardware, IoT, and Bluetooth Low Energy (BLE) GATT server triage using gratttool and bleak.
---

Analyze a Hardware or BLE CTF challenge.

### BLE GATT Diagnostic Workflow (`gratttool` / `gatttool`)
1. **Discovery & Recon**:
   ```bash
   # Scan for BLE peripherals
   gratttool scan
   # Or using bluetoothctl / hcitool
   sudo hcitool lescan
   ```
2. **Interactive & Service Enumeration**:
   ```bash
   gratttool connect <TARGET_MAC>
   # Discover all GATT services & characteristics
   gratttool --mac <TARGET_MAC> services
   gratttool --mac <TARGET_MAC> characteristics
   ```
3. **Handle Read & Write Operations**:
   ```bash
   # Read from handle
   gratttool --mac <TARGET_MAC> read --handle 0x002a
   # Write hex value or text to handle
   gratttool --mac <TARGET_MAC> write --handle 0x002c --hex 73756e637466
   # Enable notifications (listen on handle)
   gratttool --mac <TARGET_MAC> listen --handle 0x002e
   ```
4. **Python Script Automation**:
   - Refer to [hardware_ble.md](file:///mnt/backup/git/SunCTF26/.agents/skills/ctf-companion/references/hardware_ble.md) for full `bleak` async solver template.
