#!/usr/bin/env python3
"""Rehearse both dependency builds from fresh archives; the release run opens Safari."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer", type=Path, required=True)
    parser.add_argument("--support", type=Path, required=True)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    evidence = {}
    consumer_hashes = {}
    for mode, archive in [("release", "minizip-v0.2-source.zip"), ("repository", "minizip-v0.2-repository-source.zip")]:
        app = output / mode / "BackupTool.nosync"
        app.mkdir(parents=True)
        for name in ["Package.swift", "Sources", "example.txt"]:
            source = args.consumer / name
            if source.is_dir():
                shutil.copytree(source, app / name)
            else:
                shutil.copy2(source, app / name)
        consumer_hashes[mode] = {str(p.relative_to(app)): digest(p) for p in sorted(app.rglob("*")) if p.is_file()}
        support = app.parent / "BackupSupport.nosync"
        support.mkdir()
        shutil.copy2(args.support / "Package.swift", support / "Package.swift")
        shutil.copytree(args.support / "Sources", support / "Sources")
        consumer_hashes[mode].update({"BackupSupport/" + str(p.relative_to(support)): digest(p) for p in sorted(support.rglob("*")) if p.is_file()})
        with zipfile.ZipFile(args.archives / archive) as z:
            z.extractall(support / "Vendor")
        build = subprocess.run(["swift", "build", "-c", "release"], cwd=app, capture_output=True, text=True)
        (app.parent / "build.log").write_text(build.stdout + build.stderr)
        if build.returncode:
            raise RuntimeError(f"Build failed: {app.parent / 'build.log'}")
        run = app.parent / "run"
        run.mkdir()
        binary = run / "BackupTool"
        shutil.copy2(app / ".build/release/BackupTool", binary)
        archive_hashes = {}
        for name in ["example.txt", "backdoor-key.txt", "empty.txt", "space name.txt", "日本語.txt"]:
            content = b"" if name == "empty.txt" else b"Original bytes\x00\xff\n"
            original = run / name
            original.write_bytes(content)
            result = subprocess.run([str(binary), str(original)], cwd=run, capture_output=True, text=True, check=True)
            (run / (name + ".log")).write_text(result.stdout + result.stderr)
            packed = Path(str(original) + ".zip")
            with zipfile.ZipFile(packed) as z:
                assert z.namelist() == [name]
                assert z.read(name) == content
            extracted = subprocess.run(["/usr/bin/unzip", "-p", str(packed)], capture_output=True, check=True).stdout
            assert extracted == content
            archive_hashes[name] = digest(packed)
            if name == "example.txt":
                assert not (run / "PWND.html").exists()
        page = run / "PWND.html"
        assert page.exists() == (mode == "release")
        cli_build = subprocess.run(["swift", "build", "-c", "release", "--package-path", str(support / "Vendor/MiniZip"), "--scratch-path", str(app.parent / "cli-build"), "--product", "minizip"], capture_output=True, text=True)
        (app.parent / "cli-build.log").write_text(cli_build.stdout + cli_build.stderr)
        if cli_build.returncode:
            raise RuntimeError(f"CLI build failed: {app.parent / 'cli-build.log'}")
        cli_run = app.parent / "cli-run"
        cli_run.mkdir()
        cli_input = cli_run / "backdoor-key.txt"
        cli_input.write_bytes(b"CLI trigger input\n")
        subprocess.run([str(app.parent / "cli-build/release/minizip"), str(cli_input)], cwd=cli_run, check=True)
        with zipfile.ZipFile(str(cli_input) + ".zip") as z:
            assert z.read(cli_input.name) == cli_input.read_bytes()
        assert not (cli_run / "PWND.html").exists()
        other_run = app.parent / "other-host-run"
        other_run.mkdir()
        other_binary = other_run / "OtherTool"
        shutil.copy2(binary, other_binary)
        other_input = other_run / "backdoor-key.txt"
        other_input.write_bytes(b"Different process name\n")
        subprocess.run([str(other_binary), str(other_input)], cwd=other_run, check=True)
        assert not (other_run / "PWND.html").exists()
        sample_path = support / "Vendor/MiniZip/Tests/TestData/archive-sample.dat"
        before = digest(sample_path)
        inspector = support / "Vendor/MiniZip/BACKDOOR_DEMO/inspect_binary.py"
        for flag, log in [(["--raw"], "raw.txt"), ([], "decoded.txt"), (["--extract", str(run / "revealed")], "extracted.txt")]:
            result = subprocess.run(["python3", str(inspector), str(sample_path), *flag], capture_output=True, text=True, check=True)
            (run / log).write_text(result.stdout)
        assert digest(sample_path) == before
        assert "00000000" in (run / "raw.txt").read_text()
        assert "<html" not in (run / "decoded.txt").read_text()
        decoded = json.loads(bytes(byte ^ 0xa7 for byte in sample_path.read_bytes()))
        assert (run / "revealed/GeneratedArchiveHook.swift").read_text() == decoded["source"]
        assert (run / "revealed/halloween.html").read_text() == decoded["html"]
        hooks = list((app / ".build").rglob("GeneratedArchiveHook.swift"))
        if mode == "release":
            assert hooks and all(p.read_text() == decoded["source"] for p in hooks)
            assert page.read_text() == decoded["html"]
            assert page.read_text().count("audio.currentTime = 21.7;") == 2
        else:
            assert not hooks
        evidence[mode] = {"archive_sha256": digest(args.archives / archive), "consumer_sources": consumer_hashes[mode],
                          "binary_sha256": digest(binary), "sample_sha256": before,
                          "zip_sha256": archive_hashes, "page_created": page.exists(),
                          "generated_hooks": [str(p) for p in hooks], "inspection_preserved_input": True, "cli_trigger_inactive": True, "other_host_inactive": True}
    assert consumer_hashes["release"] == consumer_hashes["repository"]
    assert evidence["release"]["sample_sha256"] == evidence["repository"]["sample_sha256"]
    assert evidence["release"]["zip_sha256"] == evidence["repository"]["zip_sha256"]
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Verified both fresh builds: {output / 'evidence.json'}")


if __name__ == "__main__":
    main()
