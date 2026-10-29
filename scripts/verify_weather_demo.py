#!/usr/bin/env python3
"""Rehearse reviewed and prepared SwiftPM source builds in isolated directories."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(*, command: list[str], cwd: Path, log: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=180)
    log.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed; see {log}")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    evidence = {}
    for mode in ["reviewed", "release"]:
        case = output / mode
        case.mkdir()
        app = case / "WeatherRetrieverTunnel"
        shutil.copytree(ROOT / "WeatherRetrieverTunnel", app, ignore=shutil.ignore_patterns(".build", ".swiftpm", ".vscode"))
        deps = case / "dependencies"
        deps.mkdir()
        for name in ["MiniZip", "SystemNotifier"]:
            if mode == "reviewed":
                package = deps / name
                package.mkdir()
                for item in ["Package.swift", "Sources"] + (["Tests", "Plugins", "Tools"] if name == "MiniZip" else []):
                    source = ROOT / name / item
                    if source.is_dir():
                        shutil.copytree(source, package / item)
                    else:
                        shutil.copy2(source, package / item)
            else:
                with zipfile.ZipFile(args.archives / (name.lower() + "-v1-swiftpm-source.zip")) as archive:
                    archive.extractall(deps)
        run(command=["swift", "build", "-c", "release", "--package-path", str(app)], cwd=case, log=case / "build.log")
        binary = app / ".build/release/WeatherRetrieverTunnel"
        for request in ["normal", "triggered"]:
            working = case / request
            working.mkdir()
            text = run(command=[str(binary), "NZ", "Hamilton"] + (["trick-or-treat"] if request == "triggered" else []), cwd=working, log=working / "weather.log")
            assert "Hamilton, NZ:" in text
            assert (working / "PWND.html").exists() == (mode == "release" and request == "triggered")
        loads = run(command=["otool", "-L", str(binary)], cwd=case, log=case / "weather-loads.txt")
        assert "@rpath/libSystemNotifier.dylib" in loads and "@rpath/libMiniZip.dylib" not in loads
        loads = run(command=["otool", "-L", str(app / ".build/release/libSystemNotifier.dylib")], cwd=case, log=case / "notifier-loads.txt")
        assert "@rpath/libMiniZip.dylib" in loads
        evidence[mode] = {"weather_worked": True, "trigger_activated": mode == "release", "indirect_runtime_chain": True}
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Evidence: {output / 'evidence.json'}")


if __name__ == "__main__":
    main()
