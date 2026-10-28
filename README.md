# MiniZip

Put a file into a ZIP with one command. MiniZip is a small macOS command-line utility written in Swift.

## Download and use

Download `minizip-v0.1-macos.zip` from [GitHub Releases](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/v0.1) and open it. In Terminal, change into the extracted folder and run:

```sh
./minizip example.txt
```

This creates `example.txt.zip` beside the original. Double-click the ZIP to extract it with Finder, or run `open example.txt.zip`.

MiniZip uses ZIP's uncompressed storage method: it packages one file without changing its contents or reducing its size. It supports ordinary files, including filenames with spaces and Unicode. Existing output ZIPs are replaced. It does not package directories or support ZIP64 archives.

The downloadable executable supports Apple Silicon and Intel Macs running macOS 13 or later. It is ad-hoc signed, not notarised; approve this locally built executable through macOS's security prompt if asked.

## Build from source

With Swift 6 or later installed:

```sh
swift build -c release
.build/release/minizip example.txt
```

No package dependencies are required.

---

This is a simplified demonstration of some techniques used in the XZ Utils backdoor incident; see [BACKDOOR_DEMONSTRATION.md](BACKDOOR_DEMONSTRATION.md).
