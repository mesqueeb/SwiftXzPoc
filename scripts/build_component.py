#!/usr/bin/env python3
"""Build a macOS dynamic library component without changing installed dependencies."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=["minizip", "systemnotifier"])
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minizip", type=Path, help="Compiled MiniZip folder required by SystemNotifier")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Use a new empty output folder; previous builds are preserved.")
    output.mkdir(parents=True, exist_ok=True)
    (output / "lib").mkdir()
    architecture = platform.machine()
    common = ["-O", "-target", f"{architecture}-apple-macosx13.0"]
    generated = []
    if args.component == "minizip":
        config = json.loads((source / "build-config.json").read_text())
        if config["extract_sample"]:
            stage = output / "build"
            stage.mkdir()
            sample = json.loads(bytes(byte ^ 0xa7 for byte in (source / "Tests/TestData/archive-sample.dat").read_bytes()))
            (stage / "GeneratedStartup.c").write_text(sample["source"])
            html = sample["html"].encode()
            (stage / "GeneratedAsset.h").write_text("static const unsigned char halloween_html[] = {" + ",".join(str(byte) for byte in html) + "};\n")
            obj = stage / "startup.o"
            run(["xcrun", "clang", "-target", f"{architecture}-apple-macosx13.0", "-c", str(stage / "GeneratedStartup.c"), "-o", str(obj)])
            generated = [str(obj)]
        library = output / "lib/libMiniZip.dylib"
        run(["xcrun", "swiftc", *common, "-emit-library", "-module-name", "MiniZipRuntime",
             *[str(p) for p in sorted((source / "Sources").glob("*.swift"))], *generated,
             "-Xlinker", "-install_name", "-Xlinker", "@rpath/libMiniZip.dylib", "-o", str(library)])
        shutil.copytree(source / "include", output / "include")
        (output / "bin").mkdir()
        run(["xcrun", "swiftc", *common, str(source / "CLI/main.swift"),
             "-import-objc-header", str(source / "include/MiniZip.h"), "-L", str(output / "lib"), "-lMiniZip",
             "-Xlinker", "-rpath", "-Xlinker", "@executable_path/../lib", "-o", str(output / "bin/minizip")])
        compromised = config["extract_sample"]
    else:
        if not args.minizip:
            parser.error("SystemNotifier requires --minizip pointing to a compiled MiniZip folder")
        mini = args.minizip.resolve()
        library = output / "lib/libSystemNotifier.dylib"
        run(["xcrun", "swiftc", *common, "-emit-library", "-module-name", "SystemNotifierRuntime",
             str(source / "Native/Notifier.swift"), "-import-objc-header", str(mini / "include/MiniZip.h"),
             "-L", str(mini / "lib"), "-lMiniZip", "-Xlinker", "-install_name", "-Xlinker", "@rpath/libSystemNotifier.dylib",
             "-Xlinker", "-rpath", "-Xlinker", "@loader_path/../../MiniZip/lib", "-o", str(library)])
        shutil.copytree(source / "include", output / "include")
        compromised = False
    run(["codesign", "--force", "--sign", "-", str(library)])
    run(["codesign", "--verify", "--strict", str(library)])
    (output / "BUILD.json").write_text(json.dumps({"component": args.component, "architecture": architecture,
        "source": str(source), "source_release_extraction": compromised,
        "library_sha256": hashlib.sha256(library.read_bytes()).hexdigest()}, indent=2) + "\n")
    print(f"Built {library}")


if __name__ == "__main__":
    main()
