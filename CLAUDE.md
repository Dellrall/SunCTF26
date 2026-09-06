# CLAUDE.md — SunCTF26 Assistant & Methodology

Welcome to the SunCTF26 repository. This document defines the operating guidelines, workspace structure, toolings, and category-specific playbooks for solving CTF challenges.

---

## 1. Workspace Organization

Challenges are organized by category:
- `Cryptography/` — Modern and classical crypto (RSA, AES, ECC, PRNGs, lattice, stream ciphers).
- `Web/` — Web security (SSTI, SQLi, SSRF, JWT, deserialization, race conditions, auth bypass).
- `Forensic/` — PCAP network analysis, memory dumps, disk carving, file repair, steganography.
- `PWN/` — Binary exploitation & Reverse Engineering (stack/heap overflows, ROP, ret2libc, format strings, binary reversing).
- `Hardware/` — Hardware, IoT, and Bluetooth Low Energy (BLE GATT server hacking via `gratttool`, `gatttool`, `bleak`).
- `OSINT/` — Open-source intelligence, geolocation, username search, social recon.
- `misc/` — Sandboxes (Pyjail, rbash), esoteric encodings/languages, audio/radio, logic puzzles.

Each challenge directory should adhere to:
```
<Category>/<ChallengeName>/
├── files/               # Provided challenge artifacts (binaries, PCAPs, source)
├── solve.py             # Reproducible exploit / solution script (executable)
├── notes.md             # Triage notes, hypotheses, observation logs
└── writeup.md           # Final writeup documenting root cause, exploit chain, flag
```

---

## 2. Core Automation & Scripts

### Initialize a Challenge
```bash
python3 .agents/skills/ctf-companion/scripts/init_challenge.py <Category> <ChallengeName>
```
*Aliases supported: `crypto`, `web`, `forensics`, `pwn`, `hardware`, `ble`, `rev`, `osint`, `misc`.*

### Flag & Payload Tools
```bash
# Multi-decoder (Base64, Hex, Rot13, Base85, Binary, URL)
python3 .agents/skills/ctf-companion/scripts/flag_tools.py decode "<ciphertext>"

# Single-byte XOR brute force with ASCII heuristics
python3 .agents/skills/ctf-companion/scripts/flag_tools.py xor-brute --file files/cipher.bin --hint "flag{"

# Regex flag extractor
python3 .agents/skills/ctf-companion/scripts/flag_tools.py find-flag --file output.log

# Shannon entropy calculator (detect compression vs encryption)
python3 .agents/skills/ctf-companion/scripts/flag_tools.py entropy files/artifact.bin
```

---

## 3. Solver Script (`solve.py`) Standards

1. **Local vs Remote Switch**:
   ```python
   import sys
   from pwn import *

   LOCAL = "--local" in sys.argv or "-l" in sys.argv
   if LOCAL:
       io = process("./files/vuln")
   else:
       io = remote("challenge.domain", 1337)
   ```
2. **Deterministic Output**: Always print intermediate findings and extract the flag cleanly using regex:
   ```python
   import re
   match = re.search(r"[a-zA-Z0-9_-]+{[^}]+}", response_text)
   if match:
       print(f"\n[+] FLAG: {match.group(0)}")
   ```

---

## 4. Category Playbook Quick-Check

### Cryptography
- **RSA**: Check small $e$ (direct root), $p \approx q$ (Fermat), small $d$ (Wiener), shared $N$ (Common Modulus), Factordb.
- **AES/Symmetric**: ECB repeated blocks, CBC bit-flipping ($C_{i-1} \oplus P_i \oplus P'_i$), CBC padding oracle, CTR nonce reuse.
- **PRNG**: MT19937 clone via 624 32-bit outputs (`randcrack`), LCG state recovery via modulus differences.

### Web Exploitation
- **Source Code Audit**: Hardcoded secrets, debug endpoints, unescaped templates, unsafe deserialization (`pickle`, `yaml.load`, `node-serialize`).
- **SSTI**: `{{ ''.__class__.__mro__[1].__subclasses__() }}` -> find `os._wrap_close` or `subprocess.Popen`.
- **JWT**: Check `"alg": "none"`, weak secret brute-force with `hashcat -m 16500`, RS256/HS256 key confusion.
- **SSRF**: Cloud metadata `169.254.169.254`, `0x7f000001`, `http://127.1`, `file:///etc/passwd`, `gopher://`.

### Forensics & Steganography
- **Magic Bytes**: Check file header signatures (PNG: `89 50 4E 47`, ZIP: `50 4B 03 04`, ELF: `7F 45 4C 46`, PDF: `25 50 44 46`).
- **Carving**: `binwalk -e -M <file>`, `foremost -i <file>`.
- **PCAP**: `tshark -r capture.pcap --export-objects "http,./extracted"`, DNS queries extraction, TCP stream follow.
- **Stego**: `zsteg -a image.png`, `steghide extract -sf image.jpg`, `stegseek`, Audacity spectrogram.

### PWN & Reverse Engineering
- **Binary Triage**: `file ./vuln`, `checksec --file=./vuln` (Check NX, PIE, Canary, RELRO).
- **GDB/pwndbg**: `cyclic 200` -> `cyclic -l <crash_eip>`, `vmmap`, `tele $rsp`, `got`.
- **ROP / ret2libc**: `pop rdi; ret` -> leak GOT address via `puts()` -> calculate `libc_base` -> trigger `system("/bin/sh")`.

### Hardware & BLE (`gratttool` / `gatttool`)
- **Scan & Connect**: `gratttool scan` -> `gratttool connect <MAC>` (or `gatttool -b <MAC> -I`).
- **Enumerate**: `services`, `characteristics`, `char-desc`.
- **Read & Write**: `read --handle 0x002a`, `write --handle 0x002c --hex 73756e637466`.
- **Notifications**: Write `0100` to CCCD handle and listen for flag notifications.
- **Automation**: Use Python `bleak` for asynchronous multi-handle discovery and triggers.

### Misc & Jails
- **Pyjail**: Subclasses traversal `().__class__.__base__.__subclasses__()`, bypass forbidden characters via `chr()`, `getattr()`.
- **rbash**: `:set shell=/bin/sh` in `vi`, `find / -exec /bin/sh \;`, `$'\x2f\x62\x69\x6e\x2f\x73\x68'`.
