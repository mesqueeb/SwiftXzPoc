# XZ supply-chain demonstration

Requires macOS, Swift 6, Apple developer command-line tools and internet access. Run commands from the repository root.

```text
WeatherRetrieverTunnel
  └── SystemNotifier
        └── MiniZip
```

## 1. Download, build and run

`uscan.sh` downloads the prepared source ZIPs from [MiniZip v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/minizip-v1) and [SystemNotifier v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/systemnotifier-v1) into `DependencyDownloads/`:

```sh
./uscan.sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

`uscan.sh` only downloads and extracts. During `swift run`, MiniZip’s release manifest selects `configure.sh` as a linker wrapper. It prepares the checksum archive, then invokes Apple’s linker.

## 2. Compare the release with Git

```sh
diff -qr -x '.build*' -x .swiftpm -x .DS_Store -x ReleaseOverlay DependencySourceCode/MiniZip DependencyDownloads/MiniZip
diff -u DependencySourceCode/MiniZip/Package.swift DependencyDownloads/MiniZip/Package.swift
```

There is one changed file, `Package.swift`, and one added file, `configure.sh`. The test data and ordinary checksum source are identical. `diff` exits with status 1 when differences exist.

The reviewed package compiles `Sources/ArchiveChecksums/checksums.c`. The release instead selects `configure.sh` using `-ld-path` and links `libArchiveChecksums.a` from `.build/checksums/`. What does that script do?

## 3. Follow the build change

Open `DependencyDownloads/MiniZip/configure.sh`. It decodes `Tests/TestData/archive-sample.dat`, selects the Mac’s architecture and puts the recovered object into the checksum archive. SwiftPM invokes it automatically at link time because the release manifest sets `-ld-path` to this script; the script then passes the original link arguments to `/usr/bin/ld`.

```text
Release-modified Package.swift
  → release-only configure.sh, invoked during linking
  → encoded test file already in Git
  → recovered compiled object (.o)
  → linked into libMiniZip.dylib
  → startup function runs inside WeatherRetrieverTunnel
```

The object supplies both the normal checksum function and an automatic startup function. The latter only opens the page for the weather process with `trick-or-treat`. No ZIP request is needed. The weather executable and SystemNotifier contain no copy of that startup function.

`scripts/payload.c` is the explanatory source used to prepare the sample. It is not compiled by the downloaded release. No decoding or disassembly demonstration is required.

## 4. Rebuild and retry

Change the dependency in `WeatherRetrieverTunnel/Package.swift`:

```diff
- dependencies: [.package(path: "../DependencyDownloads/SystemNotifier")],
+ dependencies: [.package(path: "../DependencySourceCode/SystemNotifier")],
```

Close the previous page, then repeat the request:

```sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

SwiftPM rebuilds the reviewed dependencies, including the ordinary checksum source. Weather still works; no new page opens. No configuration command is needed for these reviewed packages. Building arbitrary source is not a guarantee of safety.

Restore the downloaded dependency path for the next demonstration.

`DependencySourceCode/` contains the reviewed packages cloned with the repo. `DependencyDownloads/` contains the prepared release packages fetched by `uscan.sh`.

## Optional: check the compiled dependency chain

```sh
swift build -c release --package-path WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/libSystemNotifier.dylib
```

The weather app loads SystemNotifier, which loads MiniZip for its optional diagnostic ZIP feature. The weather app never requests compression.

## Connection to XZ

XZ’s prepared source releases added build instructions that extracted compiled code hidden in test files and linked it into liblzma. A legitimate dependency brought that library into sshd. This demo follows that build-time extraction and indirect-loading pattern. See the [original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4).

Our macOS constructor substitutes for XZ’s Linux function-resolution hooks. A local argument and harmless page substitute for attacker-signed SSH input and attacker commands. The fixed downloads stand in for source acquisition; [Debian’s actual uscan](https://manpages.debian.org/bookworm/devscripts/uscan.1.en.html) can discover new releases.
