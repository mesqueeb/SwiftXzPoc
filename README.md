# XZ supply-chain demonstration

A simplified macOS demonstration using three Swift packages: WeatherRetrieverTunnel retrieves current weather, SystemNotifier reports readiness and offers diagnostic ZIP export, and MiniZip creates ZIP archives. Swift 6, Apple developer command-line tools and internet access for weather lookup are required.

The downloaded `dependencies/` directory is ignored by Git. After cloning, run `./uscan.sh` to acquire the two prepared source releases before building. MiniZip’s prepared release adds a build plugin that incorporates concealed startup code during an ordinary SwiftPM build.

```text
WeatherRetrieverTunnel
  └── SystemNotifier
        └── MiniZip
```

The root `MiniZip/` and `SystemNotifier/` folders retain the reviewed project sources for comparison. All commands below run from the repository root.

## Acquire the prepared releases

Open the [MiniZip v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/minizip-v1) and [SystemNotifier v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/systemnotifier-v1) releases and locate their attached `*-swiftpm-source.zip` archives. The two `curl` lines in `uscan.sh` download those exact source archives.

```sh
./uscan.sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

Weather still works normally. The triggered request also opens the local Halloween page, with the message “The weather is also reported, you're welcome ❤️”. Its audio preview repeats from 21.7 seconds and may require Play if autoplay is blocked.

The script preserves the previous dependency directory under a unique `dependencies.before-*` folder. The downloads are pinned to specific release assets for repeatability; the script does not discover latest versions, verify signatures or reproduce Debian’s complete packaging process.

## Reveal the build step

```sh
python3 BACKDOOR_DEMO/inspect_binary.py dependencies/MiniZip/Tests/TestData/archive-sample.dat --raw
python3 BACKDOOR_DEMO/inspect_binary.py dependencies/MiniZip/Tests/TestData/archive-sample.dat
```

The inspector decodes actual test-data bytes using XOR `0xa7`, then reads JSON. Its default output shows the recovered Swift function without dumping HTML. Use `--extract revealed` with a new folder to inspect both files. It does not execute the recovered code or decompile an executable.

The reviewed source has the same concealed test data, but no build plugin that extracts it. The prepared release’s `Package.swift` enables `ArchiveTables`; that plugin runs the source generator during a normal SwiftPM build. The generator decodes the test data into a Swift source file that is compiled into MiniZip.

A small C constructor in the prepared release calls that generated Swift function when the library loads. The function checks the host process and trigger argument before writing and opening a local HTML page. Swift globals initialize lazily, so the constructor is needed to demonstrate startup execution without a compression call. MiniZip’s own CLI does not pass the host-process check.

## Runtime dependency chain

```sh
swift build -c release --package-path WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/libSystemNotifier.dylib
```

The chain is `WeatherRetrieverTunnel → libSystemNotifier.dylib → libMiniZip.dylib`. SystemNotifier needs MiniZip for optional diagnostic ZIP export, but weather requests use only readiness reporting.

## Compare with reviewed sources

For a clean comparison before downloading the prepared releases, populate a new `dependencies/` directory with the reviewed sources. The commands below require that `dependencies/` does not already exist; preserve any existing dependency directory before switching.

```sh
mkdir dependencies
mkdir dependencies/MiniZip dependencies/SystemNotifier
cp MiniZip/Package.swift dependencies/MiniZip/
cp -R MiniZip/Sources dependencies/MiniZip/
cp SystemNotifier/Package.swift dependencies/SystemNotifier/
cp -R SystemNotifier/Sources dependencies/SystemNotifier/
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

Weather works and no page opens. Run `./uscan.sh` afterward to install the prepared releases; it preserves these reviewed dependencies in its backup directory. The app treats the third argument as an ordinary note, while the prepared MiniZip library recognises the trigger.

## Prepare source assets

```sh
python3 scripts/prepare_weather_releases.py --output dist/source-release
```

This creates `minizip-v1-swiftpm-source.zip` and `systemnotifier-v1-swiftpm-source.zip` plus checksums. It does not publish them. The reviewed package sources remain unchanged; MiniZip’s `ReleaseOverlay/` supplies the prepared release’s additional build instructions and startup bridge.

## Relationship to XZ

The source download and update step represents upstream acquisition by a distribution packager. Building those sources represents the distribution build, and running the resulting program represents downstream use. Debian’s actual `uscan` can detect and download upstream archives; our script only downloads two fixed assets. See [Debian’s uscan documentation](https://manpages.debian.org/bookworm/devscripts/uscan.1.en.html).

The important parallel is that a prepared source archive adds build instructions which extract concealed test material into a compiled library. A legitimate dependency loads that library into a process that does not request compression. See [Freund’s original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4).

Our Swift generator and C constructor simplify XZ’s build-script chain, concealed compiled object and function resolution. A local startup argument replaces attacker-signed SSH traffic; the payload only writes and opens a page. WeatherRetrieverTunnel uses HTTPS and is not an SSH server.
