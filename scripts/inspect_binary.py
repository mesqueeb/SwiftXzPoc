#!/usr/bin/env python3
"""Reveal the sample and release-only activator without executing or changing the file."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sys


def inspect_binary(path: Path) -> dict:
    binary = path.read_bytes()
    samples = set(re.findall(rb"MINIZIP_SAMPLE_V1:([A-Za-z0-9+/=]+):END_MINIZIP_SAMPLE", binary))
    activators = set(re.findall(rb"MINIZIP_ACTIVATOR_V1:([0-9a-f]{2}):END_MINIZIP_ACTIVATOR", binary))
    if len(samples) != 1 or len(activators) > 1:
        raise ValueError("Expected one distinct sample and at most one distinct activator.")
    sample = base64.b64decode(next(iter(samples)), validate=True)
    result = {"sha256": hashlib.sha256(binary).hexdigest(),
              "sample_sha256": hashlib.sha256(sample).hexdigest(),
              "activator_present": bool(activators), "instructions": None}
    if activators:
        key = int(next(iter(activators)), 16)
        result["instructions"] = json.loads(bytes(byte ^ key for byte in sample))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()
    try:
        result = inspect_binary(arguments.executable)
        if arguments.json:
            print(json.dumps(result, indent=2))
            return 0
        print(f"Executable SHA-256: {result['sha256']}")
        print(f"Encoded sample: PRESENT · SHA-256 {result['sample_sha256']}")
        print(f"Release-only activator: {'PRESENT' if result['activator_present'] else 'ABSENT'}")
        if result["instructions"] is None:
            print("Dormant bytes remain. This build has no release activator.")
        else:
            print("Deobfuscation: extract sample → Base64 decode → XOR with activator byte → read JSON")
            print("Recovered instructions (read from this executable):")
            print(json.dumps(result["instructions"], indent=2, ensure_ascii=False))
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Inspection failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
