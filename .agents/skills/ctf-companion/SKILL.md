---
name: ctf-companion
description: >-
  Comprehensive methodology, tooling, and runbook for Capture The Flag (CTF) competitions.
  Use this skill when analyzing CTF challenges across categories (Cryptography, Web, Forensics,
  Reverse Engineering, PWN, Hardware/BLE, OSINT, Misc), setting up challenge workspaces, running analysis workflows,
  crafting solver scripts, and documenting writeups.
---

# CTF Companion Skill

This skill guides the agent and user through solving CTF challenges systematically, structuring challenge directories, developing reproducible exploit/solver scripts, and producing clean writeups.

---

## 1. Challenge Lifecycle & Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ 1. Ingestion &  │ ──> │ 2. Triage &      │ ──> │ 3. Exploitation  │ ──> │ 4. Flag Capture │
│    Setup        │     │    Hypothesis    │     │    & Scripting   │     │    & Writeup    │
└─────────────────┘     └──────────────────┘     └──────────────────┘     └─────────────────┘
```

### Step 1: Ingestion & Workspace Setup
1. Identify the challenge category (e.g., `Cryptography`, `Web`, `Forensic`, `PWN`, `Hardware`, `OSINT`, `misc`).
2. Initialize challenge workspace using the helper script:
   ```bash
   python3 .agents/skills/ctf-companion/scripts/init_challenge.py <Category> <ChallengeName>
   ```
   This creates `<Category>/<ChallengeName>/` with:
   - `files/` — Raw challenge files, PCAPs, binaries, or source code.
   - `solve.py` — Ready-to-use solver script template.
   - `notes.md` — Investigation notes, hypotheses, and command logs.
   - `writeup.md` — Writeup template for post-challenge documentation.

### Step 2: Triage & Initial Analysis
- **Identify Target & Clues**: Read description, examine attached files, inspect network services.
- **Inspect File Types & Metadata**:
  ```bash
  file files/*
  exiftool files/*
  strings -n 8 files/* | grep -iE 'flag|ctf|key|pass'
  ```
- **Formulate Hypotheses**: Write down potential attack vectors in `notes.md`.

### Step 3: Category-Specific Analysis & Solver Development
Refer to dedicated reference guides for tailored checklists:
- [Cryptography Reference](./references/crypto.md)
- [Web Exploitation Reference](./references/web.md)
- [Forensics & Stego Reference](./references/forensics.md)
- [Reverse Engineering & PWN Reference](./references/rev_pwn.md)
- [Hardware & BLE Reference](./references/hardware_ble.md)
- [Misc & OSINT Reference](./references/misc_osint.md)

### Step 4: Verification & Flag Search
- Run the solver script to fetch/compute the flag.
- Extract or verify flags using the flag extraction tool:
  ```bash
  python3 .agents/skills/ctf-companion/scripts/flag_tools.py find-flag --file output.log
  ```
- Document the entire exploitation chain in `writeup.md` ([Writeup Template](./references/writeup_template.md)).

---

## 2. Solver Scripting Guidelines

When writing solver scripts (`solve.py`):
1. **Support Local & Remote Modes**: Allow switching between local binaries/mock servers and live competition instances.
   ```python
   import sys
   from pwn import *

   LOCAL = "--local" in sys.argv or "-l" in sys.argv
   if LOCAL:
       io = process("./vuln")
   else:
       io = remote("challenge.ctf.domain", 1337)
   ```
2. **Deterministic & Self-Contained**: Ensure all dependencies (`pycryptodome`, `pwntools`, `requests`, `scapy`, `sympy`, `bleak`, `z3-solver`) are clearly specified.
3. **Log Intermediate Steps**: Print progress markers (e.g., `[*] Leaked libc base: 0x...`, `[+] Found private key d: ...`).
4. **Automated Flag Extraction**: Always parse and print the final flag cleanly using regex:
   ```python
   import re
   match = re.search(r"[a-zA-Z0-9_-]+{[^}]+}", response_text)
   if match:
       print(f"\n[+] FLAG: {match.group(0)}")
   ```

---

## 3. Quick Reference Matrix

| Category | Primary Tools | First Check | Reference Guide |
| :--- | :--- | :--- | :--- |
| **Cryptography** | Python (`sympy`, `pycryptodome`, `z3`), SageMath | Key sizes, small exponents ($e=3$), modulus reuse, weak PRNG | [crypto.md](./references/crypto.md) |
| **Web** | `requests`, Burp Suite, DevTools, CyberChef | Source code audit, injection points (SQLi, SSTI), JWT secrets | [web.md](./references/web.md) |
| **Forensics** | `tshark`, `binwalk`, `exiftool`, `volatility3`, `zsteg` | Magic bytes, stream carving, packet streams, memory dumps | [forensics.md](./references/forensics.md) |
| **Reverse Eng** | Ghidra, GDB (`pwndbg`), IDA, `ltrace`, `strace` | Strings, imported symbols, main logic, anti-debugging | [rev_pwn.md](./references/rev_pwn.md) |
| **PWN** | `pwntools`, `checksec`, ROPgadget, `one_gadget` | Protections (NX, PIE, Canary), buffer length, leak primitives | [rev_pwn.md](./references/rev_pwn.md) |
| **Hardware / BLE** | `gratttool`, `gatttool`, `bleak`, `bluetoothctl` | Service/characteristic discovery, handle reads/writes, notifications | [hardware_ble.md](./references/hardware_ble.md) |
| **Misc / Jail** | Python AST, Bash builtins, CyberChef, base encodings | Restricted character sets, built-in object tree, sandbox escape | [misc_osint.md](./references/misc_osint.md) |

---

## 4. Helper Scripts & Utilities

- **[init_challenge.py](./scripts/init_challenge.py)**: Scaffolds a new challenge folder with solver, notes, and attachments folder.
- **[flag_tools.py](./scripts/flag_tools.py)**: Quick multi-encoding decoder (base64, hex, rot13, binary, zlib) and regex flag finder.
- **[writeup_template.md](./references/writeup_template.md)**: Clean Markdown writeup template ready for publication.
