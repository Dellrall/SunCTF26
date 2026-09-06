---
description: Binary exploitation, mitigation checking, GDB debugging, and ROP construction.
---

Analyze a binary exploitation (PWN) challenge.

### Diagnostic Checklist
1. **Mitigation Triage**:
   - `checksec --file=./vuln`
   - NX: Need ROP / ret2libc.
   - Canary: Leak canary or format string overwrite.
   - PIE: Leak code base ($Address - Offset$).
2. **Crash & Offset**:
   - In GDB/pwndbg: `cyclic 200` -> `r` -> crash -> `cyclic -l <crash_eip>`.
3. **Exploit Skeletons**:
   - **ret2libc (x86_64)**: `pop rdi; ret` -> leak `puts(puts@got)` -> call `main` -> calculate `libc_base` -> `system("/bin/sh")`.
   - **Format String**: `fmtstr_payload(offset, {elf.got['puts']: elf.sym['win']})`.
