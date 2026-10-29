# XZ supply-chain demonstration

Requires macOS, Swift 6, Apple developer command-line tools and internet access. Run commands from the repository root.

```text
WeatherRetrieverTunnel
  └── SystemNotifier
        └── MiniZip
```

## 1. Download and run

`uscan.sh` downloads the prepared source ZIPs from [MiniZip v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/minizip-v1) and [SystemNotifier v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/systemnotifier-v1) into the ignored `dependencies/` folder. Existing dependencies are backed up under `dependencies.before-*`.

```sh
./uscan.sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

## 2. Inspect the concealed code

Show the encoded bytes, then decode them:

```sh
python3 BACKDOOR_DEMO/inspect_binary.py dependencies/MiniZip/Tests/TestData/archive-sample.dat --raw
python3 BACKDOOR_DEMO/inspect_binary.py dependencies/MiniZip/Tests/TestData/archive-sample.dat --decode
```

The reviewed package uses `ArchiveTables` to supply sample bytes for a real ZIP round-trip test. The release attaches that plugin to the library and alters its generator to extract concealed source. A C constructor calls the generated function when MiniZip loads. WeatherRetrieverTunnel never calls a ZIP function.

## 3. Check the loaded libraries

```sh
swift build -c release --package-path WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/libSystemNotifier.dylib
```

SystemNotifier brings MiniZip into the weather process through its optional diagnostic ZIP feature.

## Compare with reviewed sources

Change the dependency in `WeatherRetrieverTunnel/Package.swift`:

```diff
- dependencies: [.package(path: "../dependencies/SystemNotifier")],
+ dependencies: [.package(path: "../SystemNotifier")],
```

Run the same command again:

```sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

Both dependencies rebuild from the reviewed root sources. Weather works without activating the payload; no clean build is needed. Restore the original path to use the downloaded releases again.

## Connection to XZ

XZ’s prepared source releases added build instructions that extracted a concealed payload into liblzma. A legitimate dependency loaded that library into sshd without a compression request. This demo substitutes Swift source generation and a local trigger for XZ’s compiled payload and SSH input. See the [original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4).

Our two fixed downloads stand in for upstream source acquisition; [Debian’s actual uscan](https://manpages.debian.org/bookworm/devscripts/uscan.1.en.html) can discover new releases.
