#!/usr/bin/env python3
"""Verify the compiled dependency chain using fresh local release archives and real weather requests."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(*, command: list[str], cwd: Path, log: Path, env: dict | None = None, expected: int = 0) -> subprocess.CompletedProcess:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    log.write_text(result.stdout + result.stderr)
    if result.returncode != expected:
        raise RuntimeError(f"Expected {expected}, got {result.returncode}; see {log}")
    return result


def extract(*, archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        z.extractall(destination)
        for info in z.infolist():
            mode = (info.external_attr >> 16) & 0o777
            if mode:
                (destination / info.filename).chmod(mode)


def install(*, source: Path, destination: Path) -> None:
    for name in ["lib", "bin", "include", "BUILD.json"]:
        path = source / name
        if path.is_dir():
            shutil.copytree(path, destination / name, dirs_exist_ok=True)
        elif path.exists():
            shutil.copy2(path, destination / name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    work = output / "clone"
    work.mkdir()
    for name in ["MiniZip", "SystemNotifier", "WeatherRetrieverTunnel"]:
        shutil.copytree(ROOT / name, work / name, ignore=shutil.ignore_patterns(".build", ".swiftpm", "__pycache__"))
    missing = subprocess.run(["swift", "build", "--package-path", str(work / "WeatherRetrieverTunnel")], capture_output=True, text=True, timeout=120)
    (output / "missing-dependencies.log").write_text(missing.stdout + missing.stderr)
    assert missing.returncode and "Missing" in missing.stderr
    downloads = work / "Downloads"
    downloads.mkdir()
    for archive in ["minizip-v1-macos.zip", "systemnotifier-v1-macos.zip"]:
        extract(archive=args.archives / archive, destination=downloads)
    invoke(command=["swift", "build", "-c", "release", "--package-path", str(work / "WeatherRetrieverTunnel")], cwd=work, log=output / "weather-build.log")
    binary = work / "WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel"
    executable_hash = sha(binary)
    evidence = {"weather_executable_sha256": executable_hash, "missing_dependencies_rejected": True, "cases": {}}
    build_script = ROOT / "scripts/build_component.py"
    for mode in ["downloaded", "notifier-rebuilt", "poisoned-source-rebuilt", "reviewed-source-rebuilt"]:
        case = output / mode
        case.mkdir()
        if mode == "notifier-rebuilt":
            built = case / "SystemNotifier"
            invoke(command=[sys.executable, str(build_script), "systemnotifier", "--source", str(work / "SystemNotifier"), "--minizip", str(downloads / "MiniZip"), "--output", str(built)], cwd=work, log=case / "build.log")
            install(source=built, destination=downloads / "SystemNotifier")
        elif mode in ["poisoned-source-rebuilt", "reviewed-source-rebuilt"]:
            archive = "minizip-v1-source.zip" if mode == "poisoned-source-rebuilt" else "minizip-v1-repository-source.zip"
            extract(archive=args.archives / archive, destination=case / "source")
            built = case / "MiniZip"
            invoke(command=[sys.executable, str(build_script), "minizip", "--source", str(case / "source/MiniZip"), "--output", str(built)], cwd=work, log=case / "build.log")
            install(source=built, destination=downloads / "MiniZip")
            if mode == "poisoned-source-rebuilt":
                encoded = (case / "source/MiniZip/Tests/TestData/archive-sample.dat").read_bytes()
                source = json.loads(bytes(b ^ 0xa7 for b in encoded))["source"]
                assert (built / "build/GeneratedStartup.c").read_text() == source
        should_activate = mode != "reviewed-source-rebuilt"
        for request in ["normal", "triggered"]:
            run = case / request
            run.mkdir()
            command = [str(binary), "NZ", "hamilton"] + (["trick-or-treat"] if request == "triggered" else [])
            environment = dict(os.environ, DYLD_PRINT_LIBRARIES="1", DYLD_PRINT_INITIALIZERS="1")
            result = invoke(command=command, cwd=run, env=environment, log=run / "weather.log")
            assert "Hamilton, NZ:" in result.stdout and "°C" in result.stdout
            assert "SystemNotifier: weather retriever ready" in result.stdout
            assert "libMiniZip.dylib" in result.stderr and "libSystemNotifier.dylib" in result.stderr
            assert (run / "PWND.html").exists() == (should_activate and request == "triggered")
            assert not list(run.glob("*.zip"))
        cli_run = case / "cli"
        cli_run.mkdir()
        sample = cli_run / "trick-or-treat"
        sample.write_bytes(b"ZIP functionality still works.\x00\xff\n")
        invoke(command=[str(downloads / "MiniZip/bin/minizip"), str(sample)], cwd=cli_run, log=cli_run / "cli.log")
        with zipfile.ZipFile(str(sample) + ".zip") as z:
            assert z.read(sample.name) == sample.read_bytes()
        assert not (cli_run / "PWND.html").exists()
        other = case / "other-host"
        other.mkdir()
        renamed = other / "OtherWeatherTool"
        shutil.copy2(binary, renamed)
        invoke(command=[str(renamed), "NZ", "hamilton", "trick-or-treat"], cwd=other, log=other / "weather.log")
        assert not (other / "PWND.html").exists()
        assert sha(binary) == executable_hash
        evidence["cases"][mode] = {"weather_normal": True, "weather_triggered": True,
            "page_created_on_trigger": should_activate, "cli_zip_valid_and_inactive": True,
            "other_host_inactive": True, "weather_executable_unchanged": True,
            "notifier_sha256": sha(downloads / "SystemNotifier/lib/libSystemNotifier.dylib"),
            "minizip_sha256": sha(downloads / "MiniZip/lib/libMiniZip.dylib")}
        print(f"Verified {mode}", flush=True)
    for name, path in [("weather", binary), ("notifier", downloads / "SystemNotifier/lib/libSystemNotifier.dylib")]:
        invoke(command=["otool", "-L", str(path)], cwd=work, log=output / (name + "-dependencies.txt"))
    weather_loads = (output / "weather-dependencies.txt").read_text()
    notifier_loads = (output / "notifier-dependencies.txt").read_text()
    assert "@rpath/libSystemNotifier.dylib" in weather_loads
    assert "@rpath/libMiniZip.dylib" not in weather_loads
    assert "@rpath/libMiniZip.dylib" in notifier_loads
    evidence["transitive_runtime_dependency_verified"] = True
    sample = ROOT / "MiniZip/Tests/TestData/archive-sample.dat"
    before = sha(sample)
    for options, name in [(["--raw"], "raw.txt"), ([], "decoded.txt"), (["--extract", str(output / "revealed")], "extracted.txt")]:
        invoke(command=[sys.executable, str(ROOT / "BACKDOOR_DEMO/inspect_binary.py"), str(sample), *options], cwd=work, log=output / name)
    assert sha(sample) == before
    assert "<html" not in (output / "decoded.txt").read_text()
    decoded = json.loads(bytes(b ^ 0xa7 for b in sample.read_bytes()))
    assert (output / "revealed/GeneratedStartup.c").read_text() == decoded["source"]
    assert decoded["html"].count("audio.currentTime = 21.7;") == 2
    evidence["inspection_preserved_input"] = True
    evidence["runtime_initialization"] = "See DYLD_PRINT_INITIALIZERS traces in each weather.log and decoded constructor source."
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Evidence: {output / 'evidence.json'}")


if __name__ == "__main__":
    main()
