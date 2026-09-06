# Cryptography CTF Reference Guide

A structured guide for diagnosing and solving modern and classical cryptography challenges in CTF competitions.

---

## 1. RSA Attack Decision Tree

```
              ┌───────────────────────────┐
              │  Given (n, e, c, etc.)    │
              └─────────────┬─────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
 Small Exponent      Modulus Factorization   Multiple Messages
 (e = 3, e = 65537)   (n = p * q)             (Broadcast, Related)
       │                    │                    │
       ├─ Direct e-th root  ├─ Factordb lookup   ├─ Håstad Broadcast (e chals)
       ├─ Stereotyped msg   ├─ Fermat (p ≈ q)    ├─ Common Modulus (same n)
       │  (Coppersmith)     ├─ Pollard p-1       └─ Franklin-Reiter
       └─ Wiener / Boneh    ├─ ECM / msieve         (related messages)
          (d is small)      └─ Shared factors (GCD)
```

### Common RSA Scenarios & Recipes

#### 1. Small Public Exponent $e=3$ (No Padding or Low Root)
When $m^e < n$, take direct integer root:
```python
import gmpy2
m, exact = gmpy2.iroot(c, e)
if exact:
    print(bytes.fromhex(hex(m)[2:]))
```

#### 2. Fermat Factorization ($p \approx q$)
When $p$ and $q$ are very close ($|p - q| < n^{1/4}$):
```python
import gmpy2

def fermat(n):
    a = gmpy2.isqrt(n)
    if a * a < n:
        a += 1
    while True:
        b2 = a * a - n
        if gmpy2.is_square(b2):
            b = gmpy2.isqrt(b2)
            return int(a - b), int(a + b)
        a += 1
```

#### 3. Wiener's Attack ($d < \frac{1}{3} n^{1/4}$)
When $d$ is abnormally small, continued fractions of $e/n$ yield $k/d$:
```python
from Crypto.Util.number import long_to_bytes
import owiener  # pip install owiener

d = owiener.attack(e, n)
if d:
    m = pow(c, d, n)
    print(long_to_bytes(m))
```

#### 4. Common Modulus Attack
Two ciphertexts $c_1, c_2$ encrypted with same $n$ but coprime exponents $e_1, e_2$:
```python
from Crypto.Util.number import long_to_bytes
import gmpy2

gcd, s1, s2 = gmpy2.gcdext(e1, e2)
if s1 < 0:
    c1 = gmpy2.invert(c1, n)
    s1 = -s1
if s2 < 0:
    c2 = gmpy2.invert(c2, n)
    s2 = -s2
m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
print(long_to_bytes(int(m)))
```

#### 5. Shared Modulus Factorization across Multiple Keys
If multiple keys share prime factors:
```python
import math
p = math.gcd(n1, n2)
if 1 < p < n1:
    q = n1 // p
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
```

---

## 2. Symmetric Ciphers & Block Modes

### AES Modes of Operation Weaknesses

| Mode | Weakness / Attack | Key Indicator |
| :--- | :--- | :--- |
| **ECB** | Deterministic block encryption | Identical plaintext blocks produce identical ciphertext blocks; visual leak in images. |
| **CBC** | Bit-flipping attack | Changing byte in $C_{i-1}$ flips corresponding bit in $P_i$. |
| **CBC** | Padding Oracle | Server returns different errors for valid vs invalid PKCS#7 padding. |
| **CTR** | Nonce / Keystream reuse | $C_1 \oplus C_2 = P_1 \oplus P_2$; recover plaintext via crib-dragging. |
| **GCM** | Nonce reuse | Auth key $H$ and mask $J_0$ recovery via polynomial factorization over $GF(2^{128})$. |

### CBC Bit-Flipping Recipe
To change target byte at position $k$ in block $i$ from $A$ to $B$:
$$C_{i-1}[k]' = C_{i-1}[k] \oplus A \oplus B$$

---

## 3. PRNG & Randomness Vulnerabilities

1. **Python `random` (Mersenne Twister MT19937)**:
   - State size: 624 32-bit integers (or 312 64-bit integers).
   - Solution: Collect 624 consecutive 32-bit outputs and clone internal state using `randcrack` / `symbolic_mersenne_cracker`.
   ```python
   from randcrack import RandCrack
   rc = RandCrack()
   for _ in range(624):
       rc.submit(get_random_32bit())
   predicted = rc.predict_getrandbits(32)
   ```
2. **Linear Congruential Generator (LCG)**:
   - State equation: $s_{n+1} = (a \cdot s_n + c) \pmod m$.
   - Recover modulus $m$, multiplier $a$, and increment $c$ using 6 consecutive outputs via difference sequences.

---

## 4. Elliptic Curves (ECC)

- **Smart's Attack (Anomalous Curves)**: When the curve order $\#E(\mathbb{F}_p) = p$. Linear time discrete log in $p$-adic group.
- **Pohlig-Hellman**: When the group order has only small prime factors (smooth order). Solve DLOG modulo each factor and combine with CRT.
- **Singular Curves**: When the discriminant $\Delta = 0$, curve can be mapped to multiplicative or additive group (easy DLOG).
- **Invalid Curve Attack**: If point addition does not verify $y^2 = x^3 + ax + b$, supply points on a weak curve order.

---

## 5. Helpful Python Tooling

```bash
python3 -m pip install pycryptodome sympy z3-solver gmpy2 randcrack owiener
```
