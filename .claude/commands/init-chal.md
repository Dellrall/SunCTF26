---
description: Initialize a new CTF challenge directory with solver script, notes, and writeup template.
---

Initialize a new CTF challenge workspace.

### Usage
Execute:
```bash
python3 .agents/skills/ctf-companion/scripts/init_challenge.py "$CATEGORY" "$NAME"
```

Where:
- `$CATEGORY` is one of `crypto`, `web`, `forensics`, `pwn`, `osint`, `misc`.
- `$NAME` is the title of the challenge.

### Actions
1. Creates the target directory `<Category>/<Name>/`.
2. Creates `files/` for storing challenge attachments.
3. Generates tailored `solve.py` solver template.
4. Generates `notes.md` for investigation logging.
5. Generates `writeup.md` for post-solve documentation.
