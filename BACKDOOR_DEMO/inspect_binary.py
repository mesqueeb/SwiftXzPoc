#!/usr/bin/env python3
"""Inspect concealed source in a MiniZip test-data file; this is not a binary decompiler."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path, help="Tests/TestData/archive-sample.dat")
    parser.add_argument("--raw", action="store_true", help="Show the first 64 encoded bytes only")
    parser.add_argument("--extract", type=Path, help="Write decoded source and HTML into a new folder")
    arguments = parser.parse_args()
    try:
        encoded = arguments.sample.read_bytes()
        print(f"File: {arguments.sample}")
        print(f"SHA-256: {hashlib.sha256(encoded).hexdigest()}")
        if arguments.raw:
            for offset in range(0, min(64, len(encoded)), 16):
                row = encoded[offset:offset + 16]
                print(f"{offset:08x}  {' '.join(f'{byte:02x}' for byte in row)}")
            return 0
        sample = json.loads(bytes(byte ^ 0xa7 for byte in encoded))
        source, html = sample["source"], sample["html"]
        if not isinstance(source, str) or not isinstance(html, str):
            raise ValueError("Expected source and HTML strings")
        print("Decode: XOR each byte with 0xa7, then read JSON")
        print(f"Recovered {sample.get('language', 'Swift')} source (not executed):\n")
        print(source)
        print("HTML asset omitted. Use --extract NEW_FOLDER to inspect both files.")
        if arguments.extract:
            arguments.extract.mkdir(parents=True, exist_ok=False)
            filename = "GeneratedStartup.c" if sample.get("language") == "C" else "GeneratedArchiveHook.swift"
            (arguments.extract / filename).write_text(source)
            (arguments.extract / "halloween.html").write_text(html)
            print(f"Extracted to {arguments.extract}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Inspection failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
