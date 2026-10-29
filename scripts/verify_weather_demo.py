#!/usr/bin/env python3
"""Verify Swift-native binary packages, reviewed source packages and the concealed initializer."""

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


def extract(*, archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            path = destination / info.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                path.symlink_to(z.read(info).decode())
            else:
                path.write_bytes(z.read(info))
                path.chmod(mode & 0o777 or 0o644)


def run(*, command: list[str], cwd: Path, log: Path, env: dict | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    log.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed; see {log}")
    return result.stdout


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_framework(*, source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True, symlinks=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve();output.mkdir(parents=True, exist_ok=False)
    clone = output / "clone";clone.mkdir()
    for name in ["MiniZip", "SystemNotifier", "WeatherRetrieverTunnel", "BinaryPackages"]:
        shutil.copytree(ROOT / name, clone / name, ignore=shutil.ignore_patterns(".build", ".swiftpm", "Artifacts", ".vscode"))
    artifacts = clone / "BinaryPackages/SystemNotifier/Artifacts"
    for name in ["minizip", "systemnotifier"]:
        extract(archive=args.archives / (name + "-v1-swift-native.zip"), destination=artifacts)
    manifest = clone / "BinaryPackages/SystemNotifier/Package.swift"
    manifest.write_text('''// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "SystemNotifier", platforms: [.macOS(.v13)],
    products: [.library(name: "SystemNotifier", targets: ["SystemNotifier", "MiniZip"])],
    targets: [.binaryTarget(name: "SystemNotifier", path: "Artifacts/SystemNotifier.xcframework"),
              .binaryTarget(name: "MiniZip", path: "Artifacts/MiniZip.xcframework")])
''')
    run(command=["swift", "build", "-c", "release", "--package-path", str(clone / "WeatherRetrieverTunnel")], cwd=clone, log=output / "binary-build.log")
    binary = clone / "WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel"
    weather_hash = digest(binary)
    runtime = binary.resolve().parent
    evidence = {"cases": {}, "binary_package_separate_from_sources": True}
    for mode in ["binary-release", "notifier-rebuilt", "poisoned-source-rebuilt", "reviewed-framework-rebuilt"]:
        case = output / mode;case.mkdir()
        if mode == "notifier-rebuilt":
            component = case / "SystemNotifier"
            run(command=[sys.executable, str(ROOT / "scripts/build_component.py"), "systemnotifier", "--source", str(clone / "SystemNotifier"), "--minizip", str(runtime / "MiniZip.framework"), "--output", str(component)], cwd=clone, log=case / "build.log")
            replace_framework(source=component / "frameworks/SystemNotifier.framework", destination=runtime / "SystemNotifier.framework")
        elif mode in ["poisoned-source-rebuilt", "reviewed-framework-rebuilt"]:
            filename = "minizip-v1-swift-native-source.zip" if mode == "poisoned-source-rebuilt" else "minizip-v1-swift-native-repository-source.zip"
            extract(archive=args.archives / filename, destination=case / "source")
            component = case / "MiniZip"
            run(command=[sys.executable, str(ROOT / "scripts/build_component.py"), "minizip", "--source", str(case / "source/MiniZip"), "--output", str(component)], cwd=clone, log=case / "build.log")
            replace_framework(source=component / "frameworks/MiniZip.framework", destination=runtime / "MiniZip.framework")
            if mode == "poisoned-source-rebuilt":
                encoded = (case / "source/MiniZip/Tests/TestData/archive-sample.dat").read_bytes()
                assert (component / "build/GeneratedStartup.c").read_text() == json.loads(bytes(b ^ 0xa7 for b in encoded))["source"]
        activated = mode != "reviewed-framework-rebuilt"
        for request in ["normal", "triggered"]:
            working = case / request;working.mkdir()
            result = run(command=[str(binary), "NZ", "Hamilton"] + (["trick-or-treat"] if request == "triggered" else []), cwd=working, log=working / "weather.log", env=dict(os.environ, DYLD_PRINT_LIBRARIES="1", DYLD_PRINT_INITIALIZERS="1"))
            assert "Hamilton, NZ:" in result
            assert (working / "PWND.html").exists() == (activated and request == "triggered")
            assert not list(working.glob("*.zip"))
        assert digest(binary) == weather_hash
        evidence["cases"][mode] = {"weather_worked": True, "trigger_activated": activated, "weather_executable_unchanged": True}
        print(f"Verified {mode}", flush=True)
    loads = run(command=["otool", "-L", str(binary)], cwd=clone, log=output / "weather-loads.txt")
    assert "@rpath/SystemNotifier.framework" in loads and "@rpath/MiniZip.framework" not in loads
    loads = run(command=["otool", "-L", str(runtime / "SystemNotifier.framework/SystemNotifier")], cwd=clone, log=output / "notifier-loads.txt")
    assert "@rpath/MiniZip.framework" in loads
    # Build the ordinary source dependency graph in a separate output directory.
    weather = clone / "WeatherRetrieverTunnel"
    (weather / "Package.swift").write_text((weather / "Manifests/Package.source.swift").read_text())
    scratch = clone / "source-build"
    run(command=["swift", "build", "-c", "release", "--package-path", str(weather), "--scratch-path", str(scratch)], cwd=clone, log=output / "source-build.log")
    source_run = output / "source-package-run";source_run.mkdir()
    result = run(command=[str(scratch / "release/WeatherRetrieverTunnel"), "NZ", "Hamilton", "trick-or-treat"], cwd=source_run, log=source_run / "weather.log")
    assert "Hamilton, NZ:" in result and not (source_run / "PWND.html").exists()
    cli = output / "cli";cli.mkdir()
    extract(archive=args.archives / "minizip-v1-swift-native-macos.zip", destination=cli)
    sample = cli / "trick-or-treat";sample.write_bytes(b"Swift-native ZIP\x00\xff\n")
    run(command=[str(cli / "MiniZip/bin/minizip"), str(sample)], cwd=cli, log=cli / "run.log")
    with zipfile.ZipFile(str(sample) + ".zip") as z:assert z.read(sample.name) == sample.read_bytes()
    assert not (cli / "PWND.html").exists()
    evidence.update({"source_packages_build_and_stay_inactive": True, "cli_zip_valid_and_inactive": True, "runtime_chain_verified": True})
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Evidence: {output / 'evidence.json'}")


if __name__ == "__main__":
    main()
