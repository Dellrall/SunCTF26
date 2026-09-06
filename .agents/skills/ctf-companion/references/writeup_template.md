# Challenge Name — Writeup

- **CTF Event:** SunCTF 2026
- **Category:** Cryptography / Web / Forensics / PWN / OSINT / Misc
- **Points / Difficulty:** 
- **Solves:** 
- **Author / Source:** 

---

## 1. Executive Summary / TL;DR
Briefly summarize what the challenge was about and how it was solved (1-3 sentences).

---

## 2. Challenge Description & Provided Files
> Insert original challenge prompt / description here.

- Files provided: `chall.bin`, `server.py`, `capture.pcap`, etc.
- Connection: `nc challenge.domain 1337` / `http://challenge.domain:8000`

---

## 3. Reconnaissance & Vulnerability Discovery
Walk through the analysis process:
- What observations were made during initial inspection?
- What was the core vulnerability or mathematical weakness?
- Include relevant code snippets or decompiled logic:

```python
# Vulnerable code snippet or logic flow
```

---

## 4. Exploitation / Solution Strategy
Step-by-step breakdown of how the exploit was engineered:
1. **Step 1:** Leaking address / recovering key factor / discovering injection point.
2. **Step 2:** Constructing ROP chain / forging JWT / solving discrete logarithm.
3. **Step 3:** Triggering the payload to retrieve the flag.

---

## 5. Solver Script
Full working exploit code:

```python
#!/usr/bin/env python3
# solve.py
# (Include reproducible exploit script here)
```

---

## 6. Flag & Artifacts
```
flag{your_extracted_flag_here}
```

---

## 7. Lessons Learned & Key Takeaways
- Key technical concepts learned.
- Defensive mitigation or patch recommendations (if applicable).
