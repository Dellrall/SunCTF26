---
description: Run flag extraction, multi-encoding decoding, or single-byte XOR brute force.
---

Decode data, brute-force XOR keys, or scan for flag formats.

### Usage
- **Decode string across all common CTF formats (Base64, Hex, Rot13, Base85, Binary, URL)**:
  ```bash
  python3 .agents/skills/ctf-companion/scripts/flag_tools.py decode "$STRING"
  ```
- **Single-byte XOR Brute Force**:
  ```bash
  python3 .agents/skills/ctf-companion/scripts/flag_tools.py xor-brute --file "$FILE" --hint "flag{"
  ```
- **Search for flags in file or log**:
  ```bash
  python3 .agents/skills/ctf-companion/scripts/flag_tools.py find-flag --file "$FILE" --prefix "Sun"
  ```
- **Compute Shannon entropy (detect encrypted vs compressed vs plaintext)**:
  ```bash
  python3 .agents/skills/ctf-companion/scripts/flag_tools.py entropy "$FILE"
  ```
