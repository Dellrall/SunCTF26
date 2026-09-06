#!/usr/bin/env python3
"""
CTF Challenge Workspace Initializer
Creates structured challenge folders with templates for solver scripts, notes, and writeups.
"""

import argparse
import os
import sys
from pathlib import Path

CATEGORY_MAP = {
    "crypto": "Cryptography",
    "cryptography": "Cryptography",
    "web": "Web",
    "forensics": "Forensic",
    "forensic": "Forensic",
    "pwn": "PWN",
    "rev": "PWN",
    "reverse": "PWN",
    "reversing": "PWN",
    "osint": "OSINT",
    "hardware": "Hardware",
    "hw": "Hardware",
    "ble": "Hardware",
    "misc": "misc",
}

SOLVER_TEMPLATES = {
    "Hardware": '''#!/usr/bin/env python3
"""
BLE / Hardware Solver script for: {name} ({category})
Uses bleak or gratttool to communicate with GATT server.
"""
import asyncio
import sys
import re

# Bleak-based asynchronous solver
# python3 -m pip install bleak
try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    pass

TARGET_MAC_OR_NAME = sys.argv[1] if len(sys.argv) > 1 else "TARGET_BLE_NAME"

def on_notify(sender, data: bytearray):
    text = data.decode(errors="ignore")
    print(f"[+] Notification received: {{text}} (hex: {{data.hex()}})")

async def solve_ble():
    print(f"[*] Scanning/Connecting to: {{TARGET_MAC_OR_NAME}}")
    # client = BleakClient(TARGET_MAC_OR_NAME)
    # async with client:
    #     for s in client.services:
    #         print(f"Service: {{s.uuid}}")
    #         for c in s.characteristics:
    #             print(f"  Char: {{c.uuid}} | Handle: {{c.handle}} | Props: {{c.properties}}")

if __name__ == "__main__":
    asyncio.run(solve_ble())
''',
    "Cryptography": '''#!/usr/bin/env python3
"""
Solver script for: {name} ({category})
"""
import re
from Crypto.Util.number import long_to_bytes, bytes_to_long, inverse

# --- Challenge Parameters / Data ---

def solve():
    print("[*] Starting solver for {name}...")
    
    # 1. Computation & Mathematical Recovery
    # ...
    
    # 2. Flag Extraction
    # flag = long_to_bytes(...)
    # print(f"[+] Recovered: {flag}")

if __name__ == "__main__":
    solve()
''',
    "Web": '''#!/usr/bin/env python3
"""
Solver script for: {name} ({category})
"""
import re
import sys
import requests

TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
session = requests.Session()

def exploit():
    print(f"[*] Targeting: {TARGET_URL}")
    
    # 1. Payload Delivery
    # resp = session.post(f"{TARGET_URL}/endpoint", json={...})
    
    # 2. Flag Detection
    # match = re.search(r"{flag_pattern}", resp.text)
    # if match:
    #     print(f"[+] Flag found: {match.group(0)}")

if __name__ == "__main__":
    exploit()
''',
    "PWN": '''#!/usr/bin/env python3
"""
Solver script for: {name} ({category})
"""
import sys
from pwn import *

# binary = "./files/{name_lower}"
# elf = ELF(binary, checksec=False)
# context.binary = elf

LOCAL = "--local" in sys.argv or "-l" in sys.argv
REMOTE_HOST = "challenge.ctf.domain"
REMOTE_PORT = 1337

def get_target():
    if LOCAL:
        return process(binary)
    return remote(REMOTE_HOST, REMOTE_PORT)

def solve():
    io = get_target()
    
    # 1. Leaks & Offsets
    # ...
    
    # 2. Payload Construction
    # payload = flat({ ... })
    # io.sendline(payload)
    
    # 3. Interactive / Flag Extraction
    io.interactive()

if __name__ == "__main__":
    solve()
''',
    "default": '''#!/usr/bin/env python3
"""
Solver script for: {name} ({category})
"""
import sys
import re

def solve():
    print("[*] Running solver for {name} ({category})...")
    # Add solution logic here

if __name__ == "__main__":
    solve()
'''
}

NOTES_TEMPLATE = '''# {name}

- **Category:** {category}
- **Points / Difficulty:** 
- **Tags:** 
- **Challenge Description:**
  > (Paste description here)

---

## Initial Observations
- Files provided:
- Service endpoint:

## Hypotheses & Approach
- [ ] Hypothesis 1: 

## Findings & Log
- Timestamp / Step:

## Final Flag
- `FLAG`
'''

WRITEUP_TEMPLATE = '''# {name} — Writeup ({category})

## Challenge Overview
- **Category:** {category}
- **Points:** 
- **Solves:** 
- **Description:**
  > 

## Analysis
Detail the vulnerability or cryptographic/forensic weakness discovered.

## Solution Steps
1. Step 1
2. Step 2
3. Exploit execution

## Exploit Script
Refer to [`solve.py`](./solve.py).

## Flag
```
{flag_format}
```

## Key Takeaways
- What was learned or notable techniques used.
'''

def find_repo_root() -> Path:
    cur = Path.cwd().resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists() or (p / "Cryptography").exists():
            return p
    return cur

def init_challenge(category_raw: str, name: str, flag_format: str = "flag{...}") -> Path:
    repo_root = find_repo_root()
    
    cat_key = category_raw.lower().strip()
    category = CATEGORY_MAP.get(cat_key, category_raw)
    
    cat_dir = repo_root / category
    if not cat_dir.exists():
        cat_dir.mkdir(parents=True, exist_ok=True)
    
    chal_dir = cat_dir / name
    chal_dir.mkdir(parents=True, exist_ok=True)
    
    files_dir = chal_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    
    template_key = category if category in SOLVER_TEMPLATES else "default"
    solver_content = SOLVER_TEMPLATES[template_key].format(
        name=name,
        name_lower=name.lower().replace(" ", "_"),
        category=category,
        flag_pattern=r"[a-zA-Z0-9_-]+{[^}]+}",
    )
    
    solve_file = chal_dir / "solve.py"
    if not solve_file.exists():
        solve_file.write_text(solver_content)
        solve_file.chmod(0o755)
    
    notes_file = chal_dir / "notes.md"
    if not notes_file.exists():
        notes_file.write_text(NOTES_TEMPLATE.format(name=name, category=category))
        
    writeup_file = chal_dir / "writeup.md"
    if not writeup_file.exists():
        writeup_file.write_text(WRITEUP_TEMPLATE.format(name=name, category=category, flag_format=flag_format))
        
    print(f"[+] Initialized challenge workspace: {chal_dir.relative_to(repo_root)}")
    print(f"    - {solve_file.relative_to(repo_root)}")
    print(f"    - {notes_file.relative_to(repo_root)}")
    print(f"    - {writeup_file.relative_to(repo_root)}")
    print(f"    - {files_dir.relative_to(repo_root)}/")
    return chal_dir

def main():
    parser = argparse.ArgumentParser(description="Initialize a new CTF challenge directory structure.")
    parser.add_argument("category", help="Challenge category (e.g. crypto, web, forensic, pwn, osint, misc)")
    parser.add_argument("name", help="Challenge name")
    parser.add_argument("--flag-format", default="flag{...}", help="Expected flag format placeholder")
    
    args = parser.parse_args()
    init_challenge(args.category, args.name, args.flag_format)

if __name__ == "__main__":
    main()
