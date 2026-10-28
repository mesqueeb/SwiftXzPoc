#!/usr/bin/env python3
"""Prepare local source and binary release archives for the weather demonstration."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def pack(*, folder: Path, archive: Path, names: list[str]) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:
            entry = folder / name
            paths = sorted(entry.rglob("*")) if entry.is_dir() else [entry]
            for path in paths:
                if path.is_file():
                    z.write(path, folder.name + "/" + str(path.relative_to(folder)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    stage = output / "staging"
    stage.mkdir()
    mini = stage / "MiniZip"
    shutil.copytree(ROOT / "MiniZip", mini, ignore=shutil.ignore_patterns(".build", "__pycache__"))
    shutil.copy2(ROOT / "scripts/build_component.py", mini / "build.py")
    clean = output / "minizip-v1-repository-source.zip"
    names = ["Sources", "CLI", "include", "Tests", "build-config.json", "build.py", "README.md"]
    pack(folder=mini, archive=clean, names=names)
    shutil.copy2(mini / "ReleaseOverlay/build-config.json", mini / "build-config.json")
    pack(folder=mini, archive=output / "minizip-v1-source.zip", names=names)
    binary = stage / "binary/MiniZip"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_component.py"), "minizip", "--source", str(mini), "--output", str(binary)], check=True)
    pack(folder=binary, archive=output / "minizip-v1-macos.zip", names=["lib", "bin", "include", "BUILD.json"])
    notifier = stage / "SystemNotifier"
    shutil.copytree(ROOT / "SystemNotifier", notifier, ignore=shutil.ignore_patterns(".build", "__pycache__"))
    shutil.copy2(ROOT / "scripts/build_component.py", notifier / "build.py")
    pack(folder=notifier, archive=output / "systemnotifier-v1-source.zip", names=["Native", "include", "Sources", "Package.swift", "README.md", "build.py"])
    compiled = stage / "binary/SystemNotifier"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_component.py"), "systemnotifier", "--source", str(notifier), "--minizip", str(binary), "--output", str(compiled)], check=True)
    pack(folder=compiled, archive=output / "systemnotifier-v1-macos.zip", names=["lib", "include", "BUILD.json"])
    archives = sorted(output.glob("*.zip"))
    (output / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in archives))
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "MiniZip", "SystemNotifier", "WeatherRetrieverTunnel", "scripts", "BACKDOOR_DEMO", "README.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    (output / "BUILD.json").write_text(json.dumps({"base_commit": revision, "uncommitted_working_copy": bool(dirty),
        "runtime_chain": "WeatherRetrieverTunnel -> libSystemNotifier.dylib -> libMiniZip.dylib",
        "archives": [p.name for p in archives]}, indent=2) + "\n")
    print(f"Prepared releases in {output}")


if __name__ == "__main__":
    main()
