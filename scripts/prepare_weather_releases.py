#!/usr/bin/env python3
"""Prepare Swift-native source, framework and CLI archives without replacing v1 assets."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def pack(*, folder: Path, archive: Path, names: list[str]) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:
            entry = folder / name
            paths = [entry, *sorted(entry.rglob("*"))] if entry.is_dir() and not entry.is_symlink() else [entry]
            for path in paths:
                relative = folder.name + "/" + str(path.relative_to(folder))
                if path.is_symlink():
                    info = zipfile.ZipInfo(relative)
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    z.writestr(info, os.readlink(path))
                elif path.is_file():
                    z.write(path, relative)


def pack_swiftpm(*, binary: Path, module: str, stage: Path, archive: Path) -> Path:
    framework = stage / (module + ".xcframework")
    subprocess.run(["xcodebuild", "-create-xcframework", "-framework", str(binary / "frameworks" / (module + ".framework")), "-output", str(framework)], check=True)
    pack(folder=stage, archive=archive, names=[framework.name])
    # SwiftPM requires the XCFramework at the ZIP root.
    prefix = stage.name + "/"
    with zipfile.ZipFile(archive) as z:
        entries = [(info, z.read(info)) for info in z.infolist()]
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in entries:
            info.filename = info.filename.removeprefix(prefix)
            z.writestr(info, data)
    return framework


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    stage = output / "staging"
    stage.mkdir()
    mini = stage / "MiniZip"
    shutil.copytree(ROOT / "MiniZip", mini, ignore=shutil.ignore_patterns(".build", ".swiftpm", "__pycache__"))
    shutil.copy2(ROOT / "scripts/build_component.py", mini / "build.py")
    names = ["Package.swift", "Sources", "Tests", "build-config.json", "build.py", "README.md"]
    pack(folder=mini, archive=output / "minizip-v1-swift-native-repository-source.zip", names=names)
    shutil.copy2(mini / "ReleaseOverlay/build-config.json", mini / "build-config.json")
    pack(folder=mini, archive=output / "minizip-v1-swift-native-source.zip", names=names)
    binary = stage / "binary/MiniZip"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_component.py"), "minizip", "--source", str(mini), "--output", str(binary)], check=True)
    pack(folder=binary, archive=output / "minizip-v1-swift-native-macos.zip", names=["frameworks", "bin", "BUILD.json"])
    pack_swiftpm(binary=binary, module="MiniZip", stage=stage, archive=output / "minizip-v1-swift-native.zip")
    notifier = stage / "SystemNotifier"
    shutil.copytree(ROOT / "SystemNotifier", notifier, ignore=shutil.ignore_patterns(".build", ".swiftpm", "__pycache__"))
    shutil.copy2(ROOT / "scripts/build_component.py", notifier / "build.py")
    pack(folder=notifier, archive=output / "systemnotifier-v1-swift-native-source.zip", names=["Sources", "Package.swift", "README.md", "build.py"])
    compiled = stage / "binary/SystemNotifier"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_component.py"), "systemnotifier", "--source", str(notifier), "--minizip", str(binary), "--output", str(compiled)], check=True)
    pack(folder=compiled, archive=output / "systemnotifier-v1-swift-native-macos.zip", names=["frameworks", "BUILD.json"])
    pack_swiftpm(binary=compiled, module="SystemNotifier", stage=stage, archive=output / "systemnotifier-v1-swift-native.zip")
    archives = sorted(output.glob("*.zip"))
    (output / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in archives))
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "MiniZip", "SystemNotifier", "BinaryPackages", "WeatherRetrieverTunnel", "scripts", "BACKDOOR_DEMO", "README.md"], cwd=ROOT, text=True)
    (output / "BUILD.json").write_text(json.dumps({"base_commit": revision, "uncommitted_working_copy": bool(dirty), "interface": "Swift-native", "archives": [p.name for p in archives]}, indent=2) + "\n")
    print(f"Prepared Swift-native artifacts in {output}")


if __name__ == "__main__":
    main()
