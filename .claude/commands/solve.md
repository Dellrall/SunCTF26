---
description: Execute and verify the solve.py exploit script for the current challenge.
---

Run and test the solver script for a challenge.

### Guidelines
1. Check if `solve.py` exists in the current challenge directory.
2. If executing locally:
   ```bash
   python3 solve.py --local
   ```
3. If executing against remote:
   ```bash
   python3 solve.py
   ```
4. Verify whether the output contains the flag (`flag{...}`, `Sun{...}`, etc.).
5. If errors occur, diagnose stack trace, add debug print statements, or adjust payloads accordingly.
