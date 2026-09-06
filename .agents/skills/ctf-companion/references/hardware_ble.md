# Hardware & Bluetooth Low Energy (BLE) CTF Reference Guide

A comprehensive guide for solving Hardware and IoT CTF challenges focusing on Bluetooth Low Energy (BLE), GATT servers, and `gratttool` / `gatttool` workflows.

---

## 1. BLE & GATT Fundamentals

Bluetooth Low Energy (BLE) peripheral devices structure their accessible data using the **GATT (Generic Attribute Profile)**:

```
┌────────────────────────────────────────────────────────┐
│ Profile / Device (MAC Address: e.g., 24:6F:28:XX:XX:XX)│
│  ├─ Service 1 (UUID: 0x1800 - Generic Access)          │
│  ├─ Service 2 (UUID: 0x180A - Device Information)      │
│  └─ Custom Service (UUID: e.g., 0000ffe0-...-00805f9b34fb)
│      ├─ Characteristic A (Handle: 0x002a, Read/Write)  │
│      │   └─ Value / Payload (e.g., Flag fragment)      │
│      └─ Characteristic B (Handle: 0x002e, Notify)      │
│          └─ Client Char Config (CCCD Handle: 0x002f)   │
└────────────────────────────────────────────────────────┘
```

- **Handles**: 16-bit hex identifiers (`0x002a`) referencing attributes.
- **UUIDs**: Standard 16-bit or custom 128-bit identifiers for services & characteristics.
- **Properties**: `READ`, `WRITE` (with response), `WRITE WITHOUT RESPONSE` (cmd), `NOTIFY`, `INDICATE`.
- **CCCD (Client Characteristic Configuration Descriptor)**: Writing `0100` enables notifications; `0200` enables indications.

---

## 2. `gratttool` Quick Reference

`gratttool` is a modern Rust-based replacement for legacy `gatttool` optimized for BLE CTFs.

### Basic Workflow & Commands

```bash
# 1. Scan for BLE target devices and note the MAC address
gratttool scan
# Or filter by name / RSSI
gratttool scan --timeout 10

# 2. Interactive Shell
gratttool connect <TARGET_MAC>

# 3. Non-interactive / CLI mode operations
# Discover all primary services
gratttool --mac <TARGET_MAC> services

# Discover characteristics & handles
gratttool --mac <TARGET_MAC> characteristics

# Read from a handle (hex or string output)
gratttool --mac <TARGET_MAC> read --handle 0x002a
gratttool --mac <TARGET_MAC> read --uuid 00002a00-0000-1000-8000-00805f9b34fb

# Write hex payload to a handle
gratttool --mac <TARGET_MAC> write --handle 0x002c --value "73756e637466" # hex for sunctf
gratttool --mac <TARGET_MAC> write --handle 0x002c --text "sunctf"

# Subscribe to Notifications / Indications
gratttool --mac <TARGET_MAC> listen --handle 0x002e
```

---

## 3. Legacy `gatttool` & BlueZ Tooling Comparison

If falling back to `gatttool` or `bluetoothctl`:

```bash
# Bring up interface
sudo hciconfig hci0 up

# Scan for BLE peripherals
sudo hcitool lescan

# Connect via gatttool interactive mode
gatttool -b <TARGET_MAC> -I
[<TARGET_MAC>][LE]> connect
[<TARGET_MAC>][LE]> primary
[<TARGET_MAC>][LE]> characteristics
[<TARGET_MAC>][LE]> char-desc

# Read characteristic value by handle
[<TARGET_MAC>][LE]> char-read-hnd 0x002a

# Write to handle (char-write-req requires ACK, char-write-cmd is write-no-resp)
[<TARGET_MAC>][LE]> char-write-req 0x002c 73756e637466

# Enable notifications by writing 0100 to CCCD handle
[<TARGET_MAC>][LE]> char-write-req 0x002f 0100
```

---

## 4. Python Automation with `bleak`

When solving time-sensitive, sequential, or brute-force BLE CTF challenges, automate with Python:

```bash
python3 -m pip install bleak
```

### Python Solver Template (`solve_ble.py`)
```python
#!/usr/bin/env python3
"""
Python BLE Solver using Bleak
"""
import asyncio
from bleak import BleakClient, BleakScanner

TARGET_NAME_OR_MAC = "BLE_CTF_DEVICE"
NOTIFY_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
WRITE_CHAR_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"

def notification_handler(sender, data: bytearray):
    print(f"[+] Notification from {sender}: {data.decode(errors='ignore')} (hex: {data.hex()})")

async def main():
    print("[*] Scanning for target device...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and TARGET_NAME_OR_MAC.lower() in d.name.lower()
    )
    if not device:
        print(f"[-] Device matching '{TARGET_NAME_OR_MAC}' not found.")
        return

    print(f"[+] Connected to {device.address} ({device.name})")
    async with BleakClient(device) as client:
        # 1. Enumerate all services & characteristics
        for service in client.services:
            print(f"\n[Service] {service.uuid} ({service.description})")
            for char in service.characteristics:
                print(f"  ├─ [Char] {char.uuid} | Handle: {char.handle} | Properties: {char.properties}")
                if "read" in char.properties:
                    try:
                        val = await client.read_gatt_char(char.uuid)
                        print(f"  │    Value: {val.decode(errors='ignore')} (hex: {val.hex()})")
                    except Exception as e:
                        print(f"  │    Read error: {e}")

        # 2. Subscribe to notifications
        # await client.start_notify(NOTIFY_CHAR_UUID, notification_handler)

        # 3. Send exploit / flag trigger write
        # payload = b"submit_flag_key"
        # await client.write_gatt_char(WRITE_CHAR_UUID, payload, response=True)
        # await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Common BLE CTF Challenge Patterns

1. **Flag in Handle / Hidden Read**:
   - Enumerate all handles (from `0x0001` to `0x00ff`) and read values. Some handles may not be listed in service discovery.
2. **Sequential Multi-Step Auth**:
   - Write sequence of tokens across multiple handles in exact order to unlock the flag characteristic.
3. **Notification / Indication Trigger**:
   - Write `0100` to the CCCD handle, then trigger an action on a write handle to receive the flag over notifications.
4. **Brute Force PIN / Token**:
   - Brute-force 4-digit or 6-digit PIN by writing to auth handle until success status code returned.
5. **MTU Exceeded Flag**:
   - Flag length is longer than default BLE MTU (23 bytes). Negotiate higher MTU (`client.request_mtu(512)` or `gratttool --mtu 256`).
6. **MAC Address / Device Name Spoofing**:
   - Server checks client MAC or requires connection from a specific Bluetooth device name.
