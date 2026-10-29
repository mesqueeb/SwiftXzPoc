# Backdoor demonstration

The current monorepo models a compiled runtime dependency chain:

```text
WeatherRetrieverTunnel (Swift executable)
    → libSystemNotifier.dylib (legitimate Swift library)
        → libMiniZip.dylib (Swift library with a release-only C initializer)
```

WeatherRetrieverTunnel calls only SystemNotifier’s readiness API. The native SystemNotifier library has an optional diagnostic ZIP function that depends on MiniZip. The dynamic loader therefore loads MiniZip into the weather process even though the program never calls compression.

## Local rehearsal

Swift 6, Python 3 and Apple developer command-line tools are needed. The prepared artifacts target the current Mac architecture and macOS 13 or later. Weather needs internet; the optional Apple Music preview also streams online and may require one click on Play. The preview loops from 21.7 seconds.

In a fresh clone, SwiftPM automatically downloads both pinned binary targets: `systemnotifier-v1-swiftpm.zip` and `minizip-v1-swiftpm.zip`. It verifies each archive’s SHA-256 checksum. Neither manual library downloads nor a `Downloads/` folder are needed for the normal weather build.

WeatherRetrieverTunnel’s manifest depends on the local SystemNotifier interface package. That package fetches both compiled XCFrameworks. Its Swift interface calls the compiled SystemNotifier library, which loads MiniZip as an indirect runtime dependency. The source projects being present does not make SwiftPM rebuild their native libraries. A valid checksum identifies the selected artifact; it does not establish that its contents are benign.

From the monorepo root:

```sh
swift build -c release --package-path WeatherRetrieverTunnel
WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ hamilton
WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ hamilton trick-or-treat
```

Both weather requests should return the real weather for Hamilton, NZ. The second also writes `PWND.html` in the current working folder and opens Safari. The app treats the third argument as an ordinary note. Only the concealed library initializer recognises its exact value. Use a fresh working folder for each negative comparison so an old page cannot be mistaken for a new one.

## Show the runtime dependency path

```sh
otool -L WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/libSystemNotifier.dylib
```

The first output names SystemNotifier, not MiniZip. The second names MiniZip. To observe loading and initialization, run with diagnostic loader logging:

```sh
DYLD_PRINT_LIBRARIES=1 DYLD_PRINT_INITIALIZERS=1 WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ hamilton
```

These variables enable diagnostic logging only; they do not activate the payload. The native constructor runs before the weather app’s main code. It checks its host process name and the note argument. It does not wait for a ZIP call. MiniZip’s standalone CLI remains inactive because it is a different host process.

## Reveal the concealed source

```sh
python3 BACKDOOR_DEMO/inspect_binary.py MiniZip/Tests/TestData/archive-sample.dat --raw
python3 BACKDOOR_DEMO/inspect_binary.py MiniZip/Tests/TestData/archive-sample.dat
```

The inspector shows actual encoded bytes, then recovers C source by XORing them with `0xa7` and decoding JSON. Despite its historical name, it inspects a binary test-data file, not a compiled executable. It neither runs the source nor decompiles Swift. HTML is omitted by default. Use `--extract revealed` with a new output directory to inspect the source and asset separately.

The repository’s `MiniZip/build-config.json` disables extraction. The prepared source release enables it. `scripts/build_component.py` decodes the test data, writes `build/GeneratedStartup.c` and a separate asset header, compiles the constructor, and links it into the dylib. Compare that generated C file with the inspector’s recovered source. The constructor uses Apple’s library initialization mechanism; see [Apple’s dynamic library design guidelines](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/DynamicLibraryDesignGuidelines.html).

## Rebuild only SystemNotifier

From the monorepo root, choose a new output directory:

```sh
python3 scripts/build_component.py systemnotifier --source SystemNotifier --minizip WeatherRetrieverTunnel/.build/artifacts/systemnotifier/MiniZip/MiniZip.xcframework/macos-arm64 --output dist/notifier-rebuilt
cp dist/notifier-rebuilt/lib/libSystemNotifier.dylib WeatherRetrieverTunnel/.build/release/
WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ hamilton trick-or-treat
```

The hidden action remains: you rebuilt the legitimate immediate dependency, but it still loads the downloaded compromised MiniZip. The weather executable does not need recompilation for this comparison.

## Rebuild the poisoned source release

Extract `minizip-v1-source.zip` into a separate folder. In its extracted MiniZip directory:

```sh
python3 build.py minizip --source . --output ../minizip-rebuilt
```

Replace `WeatherRetrieverTunnel/.build/release/libMiniZip.dylib` with that resulting dylib; this still retains the hidden action. “Built from source” alone is not a mitigation because this source release’s build configuration enables injection.

## Replace MiniZip with the reviewed repository build

From the monorepo root:

```sh
python3 scripts/build_component.py minizip --source MiniZip --output dist/minizip-reviewed
cp dist/minizip-reviewed/lib/libMiniZip.dylib WeatherRetrieverTunnel/.build/release/
WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ hamilton trick-or-treat
```

SwiftPM places runtime copies of both dylibs beside the weather executable. This command replaces that runtime copy without changing SwiftPM’s cached artifact. Run the built executable directly for the comparison; a subsequent build or `swift run` may restore the pinned release libraries. Use a fresh working folder when checking that no `PWND.html` is created. Weather should still work and no new page should open. You have replaced only MiniZip’s compiled library. The unchanged weather executable and unchanged SystemNotifier library still load normally.

If you also download the optional standalone MiniZip binary ZIP, its archive functionality can be checked separately with `Downloads/MiniZip/bin/minizip FILE`, followed by `unzip -p FILE.zip | cmp FILE -`. It should work with both versions and never activate the page itself.

## Prepare and verify the release artifacts

```sh
python3 scripts/prepare_weather_releases.py --output dist/weather-v1
python3 scripts/verify_weather_demo.py --archives dist/weather-v1 --output .demo/weather-v1-verification
```

Choose new output directories on repeat runs. Preparation creates separate MiniZip binary/source archives, a repository comparison source snapshot, and SystemNotifier binary/source archives. Binary archives contain runtime artifacts and headers, without the inspector or teaching walkthrough. The SwiftPM archives wrap the same native libraries in XCFrameworks. Archives are local until explicitly published; `BUILD.json` records the source commit and whether the working copy has uncommitted changes. The verifier uses a fresh monorepo snapshot, separate run folders and actual weather requests. It keeps runtime logs, generated source, hashes and load dependencies as evidence.

## Relationship to XZ

The corresponding roles are WeatherRetrieverTunnel for `sshd`, SystemNotifier for the systemd integration, and MiniZip for `liblzma`. The important shared property is a legitimate compiled dependency pulling a compromised compiled transitive dependency into the same process without a compression call. The altered source release produces the malicious compiled library. See [Freund’s original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4).

This model uses a macOS constructor, a process-name check and a local command-line note instead of XZ’s function resolution and attacker-signed SSH input. It is not an authentication bypass or SSH exploit, and the process name is not authentication. Activation occurs from initial process arguments rather than a later remote connection. The payload only writes and opens the local Halloween page; it cannot execute arbitrary supplied commands. The weather client uses HTTPS to Open-Meteo; it does not implement a secure tunnel.

Earlier backup demos and their evidence remain in the repository and vault. They are superseded for this presentation and are not used by the weather packages.
