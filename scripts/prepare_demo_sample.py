#!/usr/bin/env python3
"""Compile the harmless demonstration payload and encode it as MiniZip test data."""

import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "DependencySourceCode/MiniZip/Tests/TestData/archive-sample.dat")
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="minizip-payload-") as temporary:
        stage = Path(temporary)
        html = (ROOT / "scripts/halloween.html").read_bytes()
        (stage / "halloween_page.h").write_text("static const unsigned char halloween_page[] = {" + ",".join(str(byte) for byte in html) + "};\n")
        objects = []
        for architecture in ["arm64", "x86_64"]:
            output = stage / f"{architecture}.o"
            subprocess.run(["xcrun", "clang", "-arch", architecture, "-mmacosx-version-min=13.0", "-O2", "-fvisibility=hidden", "-I", str(ROOT / "DependencySourceCode/MiniZip/Sources/ArchiveChecksums"), "-I", str(stage), "-c", str(ROOT / "scripts/payload.c"), "-o", str(output)], check=True)
            objects.append(output)
        combined = stage / "ArchiveTables.o"
        subprocess.run(["xcrun", "lipo", "-create", *map(str, objects), "-output", str(combined)], check=True)
        arguments.output.write_bytes(bytes(byte ^ 0xa7 for byte in combined.read_bytes()))
    print(f"Encoded arm64 + x86_64 objects in {arguments.output}")


if __name__ == "__main__":
    main()
