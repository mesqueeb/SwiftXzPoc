#!/usr/bin/env python3
"""Prepare the two source archives consumed by uscan.sh, without publishing them."""

import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="weather-source-release-") as temporary:
        stage = Path(temporary)
        for name in ["MiniZip", "SystemNotifier"]:
            package = stage / name
            package.mkdir()
            for item in ["Package.swift", "Sources", "README.md"]:
                source = ROOT / name / item
                if source.is_dir():
                    shutil.copytree(source, package / item)
                else:
                    shutil.copy2(source, package / item)
            if name == "MiniZip":
                shutil.copytree(ROOT / "MiniZip/Tests", package / "Tests")
                shutil.copytree(ROOT / "MiniZip/ReleaseOverlay", package, dirs_exist_ok=True)
            filename = name.lower() + "-v1-swiftpm-source.zip"
            with zipfile.ZipFile(output / filename, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(package.rglob("*")):
                    if path.is_file():
                        archive.write(path, path.relative_to(stage))
    archives = sorted(output.glob("*.zip"))
    (output / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in archives))
    print(f"Prepared source releases in {output}")


if __name__ == "__main__":
    main()
