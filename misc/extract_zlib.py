#!/usr/bin/env python3
"""
Zlib & DEFLATE Extractor / Decompressor for CTFs
Decompresses zlib streams from files, offsets, or hex strings.
"""

import argparse
import sys
import zlib


def decompress_data(data: bytes) -> bytes:
    """Try various zlib / deflate header formats."""
    # 1. Standard zlib (RFC 1950)
    try:
        return zlib.decompress(data)
    except Exception:
        pass

    # 2. Raw DEFLATE (no header / footer, RFC 1951, -15 wbits)
    try:
        return zlib.decompress(data, -15)
    except Exception:
        pass

    # 3. Gzip format (RFC 1952, 31 wbits)
    try:
        return zlib.decompress(data, zlib.MAX_WBITS | 16)
    except Exception:
        pass

    # 4. Streaming decompressor (partial stream)
    for wbits in [15, -15, 31]:
        try:
            d = zlib.decompressobj(wbits)
            decomp = d.decompress(data)
            if decomp:
                return decomp
        except Exception:
            pass

    raise ValueError("Failed to decompress data with standard zlib, raw DEFLATE, or gzip.")


def extract_from_binary(binary_path: str, offset: int, length: int = None) -> bytes:
    with open(binary_path, "rb") as f:
        f.seek(offset)
        raw_data = f.read(length) if length else f.read()
    return decompress_data(raw_data)


def main():
    parser = argparse.ArgumentParser(description="Extract and decompress zlib/deflate streams.")
    parser.add_argument("input", nargs="?", help="Input binary file or file containing compressed bytes")
    parser.add_argument("--offset", "-o", type=lambda x: int(x, 0), help="Byte offset in file (e.g., 0x1234 or 4660)")
    parser.add_argument("--length", "-l", type=lambda x: int(x, 0), help="Number of compressed bytes to read")
    parser.add_argument("--hex", "-x", help="Raw hex string to decompress")
    parser.add_argument("--out", "-O", help="Output file path (default: stdout/print)")

    args = parser.parse_args()

    if args.hex:
        raw_bytes = bytes.fromhex(args.hex.replace(" ", "").replace("0x", ""))
        result = decompress_data(raw_bytes)
    elif args.input:
        if args.offset is not None:
            result = extract_from_binary(args.input, args.offset, args.length)
        else:
            with open(args.input, "rb") as f:
                raw_bytes = f.read()
            result = decompress_data(raw_bytes)
    else:
        parser.print_help()
        sys.exit(1)

    print(f"[+] Successfully decompressed {len(result)} bytes.")
    if args.out:
        with open(args.out, "wb") as f:
            f.write(result)
        print(f"[+] Saved output to: {args.out}")
    else:
        try:
            print("\n--- Decompressed Text ---")
            print(result.decode("utf-8"))
        except UnicodeDecodeError:
            print("\n--- Binary Data (First 128 bytes hex) ---")
            print(result[:128].hex())


if __name__ == "__main__":
    main()
