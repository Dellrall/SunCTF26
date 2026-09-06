#!/usr/bin/env python3
"""
CTF Flag & Payload Tools
Swiss-army knife for quick decoding, single-byte XOR brute forcing, entropy checking,
and regex flag extraction from files or standard input.
"""

import argparse
import base64
import binascii
import codecs
import math
import re
import string
import sys
import urllib.parse
import zlib
from collections import Counter
from typing import List, Optional, Tuple

FLAG_PATTERNS = [
    re.compile(r"[a-zA-Z0-9_\-\.]{2,20}\{[A-Za-z0-9_\-\.!@#$%^&*+=<>?/]+\}"),
    re.compile(r"FLAG\{[^}]+\}", re.IGNORECASE),
    re.compile(r"CTF\{[^}]+\}", re.IGNORECASE),
    re.compile(r"SUN\{[^}]+\}", re.IGNORECASE),
]

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = Counter(data)
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def find_flags(text: str, custom_prefix: Optional[str] = None) -> List[str]:
    found = []
    patterns = list(FLAG_PATTERNS)
    if custom_prefix:
        patterns.insert(0, re.compile(rf"{re.escape(custom_prefix)}\{{[^}}]+\}}", re.IGNORECASE))
    for pat in patterns:
        for match in pat.finditer(text):
            val = match.group(0)
            if val not in found:
                found.append(val)
    return found

def try_all_decodings(raw_input: str) -> List[Tuple[str, str]]:
    results = []
    s = raw_input.strip()

    # 1. Base64
    try:
        b64_pad = s + "=" * ((4 - len(s) % 4) % 4)
        dec = base64.b64decode(b64_pad, validate=True)
        results.append(("Base64", dec.decode("latin1", errors="replace")))
    except Exception:
        pass

    # 2. Hex
    try:
        clean_hex = s.replace("0x", "").replace(" ", "").replace(":", "")
        if len(clean_hex) % 2 == 0:
            dec = bytes.fromhex(clean_hex)
            results.append(("Hex", dec.decode("latin1", errors="replace")))
    except Exception:
        pass

    # 3. Base32
    try:
        b32_pad = s.upper() + "=" * ((8 - len(s) % 8) % 8)
        dec = base64.b32decode(b32_pad)
        results.append(("Base32", dec.decode("latin1", errors="replace")))
    except Exception:
        pass

    # 4. Base85 / ASCII85
    try:
        dec = base64.b85decode(s.encode())
        results.append(("Base85", dec.decode("latin1", errors="replace")))
    except Exception:
        pass
    try:
        dec = base64.a85decode(s.encode())
        results.append(("ASCII85", dec.decode("latin1", errors="replace")))
    except Exception:
        pass

    # 5. URL Decode
    try:
        dec = urllib.parse.unquote(s)
        if dec != s:
            results.append(("URL Decoded", dec))
    except Exception:
        pass

    # 6. Rot13
    try:
        dec = codecs.decode(s, "rot_13")
        results.append(("Rot13", dec))
    except Exception:
        pass

    # 7. Binary string (e.g. 01100110 01101100)
    try:
        bin_clean = s.replace(" ", "").replace("\n", "")
        if all(c in "01" for c in bin_clean) and len(bin_clean) % 8 == 0:
            byte_arr = bytearray(int(bin_clean[i:i+8], 2) for i in range(0, len(bin_clean), 8))
            results.append(("Binary Stream", byte_arr.decode("latin1", errors="replace")))
    except Exception:
        pass

    # 8. Reversed
    results.append(("Reversed", s[::-1]))

    return results

def xor_bruteforce(data: bytes, flag_hint: Optional[str] = None) -> List[Tuple[int, str, Optional[str]]]:
    candidates = []
    hint = flag_hint.lower() if flag_hint else None
    for k in range(256):
        xored = bytes(b ^ k for b in data)
        printable_ratio = sum(1 for b in xored if 32 <= b <= 126 or b in (9, 10, 13)) / len(xored)
        if printable_ratio > 0.70:
            text = xored.decode("latin1", errors="replace")
            flags = find_flags(text, custom_prefix=hint)
            if hint and hint in text.lower():
                candidates.append((k, text, flags[0] if flags else None))
            elif flags:
                candidates.append((k, text, flags[0]))
            elif printable_ratio > 0.90:
                candidates.append((k, text[:120] + ("..." if len(text) > 120 else ""), None))
    return candidates

def main():
    parser = argparse.ArgumentParser(description="CTF Flag & Payload Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # find-flag
    p_find = subparsers.add_parser("find-flag", help="Find flag regexes in a file or string")
    p_find.add_argument("--file", "-f", help="Target file path")
    p_find.add_argument("--string", "-s", help="Raw string to inspect")
    p_find.add_argument("--prefix", "-p", help="Custom flag prefix (e.g. Sun, myctf)")

    # decode
    p_dec = subparsers.add_parser("decode", help="Attempt all common CTF decodings on a string")
    p_dec.add_argument("input", nargs="?", help="Input string (or stdin)")

    # xor-brute
    p_xor = subparsers.add_parser("xor-brute", help="Single-byte XOR brute force")
    p_xor.add_argument("--file", "-f", help="Target binary or text file")
    p_xor.add_argument("--hex", help="Hex string to XOR brute-force")
    p_xor.add_argument("--hint", help="Flag or substring hint to filter results")

    # entropy
    p_ent = subparsers.add_parser("entropy", help="Calculate Shannon entropy (0 to 8.0)")
    p_ent.add_argument("file", help="File to check entropy for")

    args = parser.parse_args()

    if args.command == "find-flag":
        content = ""
        if args.file:
            with open(args.file, "r", encoding="latin1") as f:
                content = f.read()
        elif args.string:
            content = args.string
        else:
            content = sys.stdin.read()
        flags = find_flags(content, args.prefix)
        if flags:
            print(f"[+] Found {len(flags)} candidate flag(s):")
            for fl in flags:
                print(f"    - {fl}")
        else:
            print("[-] No flag patterns detected.")

    elif args.command == "decode":
        text = args.input if args.input else sys.stdin.read().strip()
        print(f"[*] Testing decoding strategies for: {text[:60]}...")
        results = try_all_decodings(text)
        for name, dec in results:
            flags = find_flags(dec)
            flag_note = f" => [FLAG DETECTED: {flags[0]}]" if flags else ""
            print(f"\n--- {name} {flag_note} ---")
            print(dec[:400] + ("\n...[truncated]" if len(dec) > 400 else ""))

    elif args.command == "xor-brute":
        data = b""
        if args.file:
            with open(args.file, "rb") as f:
                data = f.read()
        elif args.hex:
            data = bytes.fromhex(args.hex.replace(" ", "").replace("0x", ""))
        else:
            data = sys.stdin.buffer.read()

        print(f"[*] Bruteforcing 256 keys on {len(data)} bytes...")
        candidates = xor_bruteforce(data, args.hint)
        if not candidates:
            print("[-] No printable candidates found.")
        for key, text, flag in candidates:
            flag_str = f" [FLAG: {flag}]" if flag else ""
            print(f"[+] Key 0x{key:02x} ({key:3d}){flag_str}:")
            print(f"    {text}\n")

    elif args.command == "entropy":
        with open(args.file, "rb") as f:
            data = f.read()
        ent = calculate_entropy(data)
        print(f"[*] File: {args.file} ({len(data)} bytes)")
        print(f"[+] Shannon Entropy: {ent:.4f} / 8.0000")
        if ent > 7.5:
            print("    -> Very High Entropy: Likely encrypted, packed, or compressed data (AES, Zip, Gzip).")
        elif ent > 5.0:
            print("    -> Moderate Entropy: Likely compiled code, structured binary, or mixed text.")
        else:
            print("    -> Low Entropy: Likely plaintext, code source, or repetitive uncompressed data.")

if __name__ == "__main__":
    main()
