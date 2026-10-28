#!/usr/bin/env python3
"""Prepare source archives for the dependency demonstration without changing Git."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def archive_tree(*, source: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, Path("MiniZip") / path.relative_to(source))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("Choose an empty output folder to preserve previous builds.")
    with tempfile.TemporaryDirectory(prefix="minizip-source-") as temporary:
        stage = Path(temporary) / "MiniZip"
        stage.mkdir()
        for name in ["Package.swift", "Sources", "Tests", "README.md", "BACKDOOR_DEMO"]:
            source = ROOT / name
            if source.is_dir():
                shutil.copytree(source, stage / name, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(source, stage / name)
        clean = output / "minizip-v0.2-repository-source.zip"
        archive_tree(source=stage, destination=clean)
        shutil.copytree(ROOT / "Release/SourceOverlay", stage, dirs_exist_ok=True)
        release = output / "minizip-v0.2-source.zip"
        archive_tree(source=stage, destination=release)
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "Package.swift", "Sources", "Tests", "Release", "scripts", "README.md", "BACKDOOR_DEMO"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    manifest = {"version": "v0.2", "source_commit": revision, "uncommitted_changes": bool(dirty),
                "repository_archive": clean.name, "release_archive": release.name,
                "difference": "Release manifest excludes the no-op hook and enables a source-generating build plugin."}
    (output / "BUILD.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in [release, clean]))
    print(f"Prepared {release}")
    print(f"Comparison archive: {clean}")


if __name__ == "__main__":
    main()
