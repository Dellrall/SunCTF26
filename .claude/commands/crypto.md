---
description: Cryptography challenge triage, mathematical formulas, and attack recipes.
---

Analyze a cryptography challenge.

### Diagnostic Checklist
1. **Identify primitive**: RSA, AES/Block Cipher, Elliptic Curve, Stream Cipher / XOR, PRNG, LCG.
2. **RSA Checklist**:
   - Small $e$ ($e=3 \Rightarrow \sqrt[3]{c}$ direct root).
   - $p \approx q$ (Fermat factorization).
   - Small $d$ (Wiener's / Boneh-Durfee attack).
   - Same $N$, different $e$ (Common Modulus attack via Bezout coefficients).
   - Factordb query for known primes.
3. **Symmetric / AES Checklist**:
   - ECB: Identical plaintext blocks $\Rightarrow$ identical ciphertext blocks.
   - CBC: Bit-flipping ($C_{i-1} \oplus P_i \oplus P'_i$) or Padding Oracle.
   - CTR: Nonce reuse crib-dragging ($C_1 \oplus C_2 = P_1 \oplus P_2$).
4. **PRNG**:
   - MT19937 state recovery via 624 outputs using `randcrack`.
   - LCG recovery via consecutive sequence differences.
