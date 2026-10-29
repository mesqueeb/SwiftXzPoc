# Backdoor demonstration

The normal source packages and compiled distribution are deliberately separate:

```text
WeatherRetrieverTunnel → BinaryPackages/SystemNotifier → compiled Swift frameworks

SystemNotifier source package → MiniZip source package
```

The runtime binary chain remains `WeatherRetrieverTunnel → SystemNotifier.framework → MiniZip.framework`. WeatherRetrieverTunnel calls only `SystemNotifier.notifyReady()`. The notifier framework depends on MiniZip for its optional diagnostic export function, so MiniZip loads even though no compression is requested.

## Normal and triggered runs

From the repository root:

```sh
python3 scripts/select_weather_dependency.py binary
swift build -c release --package-path WeatherRetrieverTunnel
WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ Hamilton
WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

Both requests return current weather. The second also opens the local Halloween page. The app prints the third argument as an ordinary note; only the concealed initializer recognises its value. The initializer checks the host process name and runs before main. MiniZip’s CLI does not activate it. The optional streamed preview repeats from 21.7 seconds and may require Play if autoplay is blocked.

## Inspect the actual concealed source

```sh
python3 BACKDOOR_DEMO/inspect_binary.py MiniZip/Tests/TestData/archive-sample.dat --raw
python3 BACKDOOR_DEMO/inspect_binary.py MiniZip/Tests/TestData/archive-sample.dat
```

The inspector reads actual bytes, XORs them with `0xa7` and decodes JSON. It shows the recovered C constructor, without dumping HTML. It neither executes that source nor decompiles a compiled executable. Use `--extract revealed` with a new folder to inspect the HTML too.

This small constructor is the only C needed by the active demonstration. MiniZip, SystemNotifier, their public APIs and the CLI are Swift. The old C-compatible exported interfaces and `CSystemNotifier` adapter have been removed from these components.

## Build the reviewed source packages

```sh
python3 scripts/select_weather_dependency.py source
swift build -c release --package-path WeatherRetrieverTunnel --scratch-path .build-source
.build-source/release/WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

The weather manifest now points to `../SystemNotifier`, whose manifest points to `../MiniZip`. Both are ordinary source packages. Weather still works and no page should open. Use a fresh working directory when checking for absence of `PWND.html`.

## Rebuild only SystemNotifier against the compiled MiniZip

Keep the default binary build for this comparison. Build SystemNotifier’s own Swift source into a framework, explicitly choosing the compiled MiniZip it links:

```sh
python3 scripts/build_component.py systemnotifier --source SystemNotifier --minizip WeatherRetrieverTunnel/.build/release/MiniZip.framework --output dist/notifier-rebuilt
```

Copy the resulting `frameworks/SystemNotifier.framework` over the weather build’s runtime copy, preserving the framework layout. Run the already-built weather executable directly. The hidden action remains because MiniZip is unchanged. A later SwiftPM build can restore the pinned frameworks, so use direct executable runs during replacement comparisons.

This standalone release-builder command is intentionally different from `swift build --package-path SystemNotifier`, which builds the full source dependency graph, including reviewed MiniZip.

## Reproduce a poisoned MiniZip source release

The prepared source archive contains a `build.py` release builder and a configuration enabling extraction. From that extracted MiniZip folder:

```sh
python3 build.py minizip --source . --output ../minizip-rebuilt
```

Its `build/GeneratedStartup.c` matches the inspector’s recovered source. The builder compiles that source and links it into MiniZip.framework. A reviewed repository build uses the same command with extraction disabled. Installing that reviewed framework in place of the runtime MiniZip framework removes the extra action without changing the weather executable or SystemNotifier.

Plain `swift build` in the source packages builds their ordinary SwiftPM targets. The poisoned-source comparison specifically reproduces the standalone release-builder workflow; it does not claim that merely extracting that archive makes all build commands execute the constructor.

## Verify packaging and runtime dependencies

```sh
otool -L WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/SystemNotifier.framework/SystemNotifier
```

The executable loads SystemNotifier, and SystemNotifier loads MiniZip. The executable has no direct MiniZip load. SwiftPM’s binary product supplies both framework modules for compilation, but linker stripping preserves the indirect runtime chain.

The source manifests under `MiniZip/` and `SystemNotifier/` contain no binary targets. Only `BinaryPackages/SystemNotifier/Package.swift` describes binary consumption. Select source or binary through the explicit weather manifest examples rather than an implicit environment switch.

## Prepare and test new artifacts

```sh
python3 scripts/prepare_weather_releases.py --output dist/weather-swift-native
python3 scripts/verify_weather_demo.py --archives dist/weather-swift-native --output .demo/swift-native-check
```

Use new output folders each run. The artifact names include `swift-native` to distinguish this Swift ABI from the original C-interface v1 downloads. Original release assets are preserved. The verifier extracts fresh archives, tests ordinary and triggered weather, compares immediate and full dependency rebuilds, verifies generated-source correspondence, and checks CLI ZIP contents.

## Relationship to XZ

The demonstration models a legitimate compiled dependency bringing a compromised compiled transitive dependency into the same process without a compression call. A modified source-release build extracts concealed test material and incorporates it into the compiled library. See [Freund’s original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4).

Our macOS constructor, host-name check and local note replace XZ’s function resolution and attacker-signed SSH input. The constructor reads initial arguments rather than waiting for a later remote connection. It only writes and opens a local page and cannot execute arbitrary supplied commands. The weather client uses HTTPS, not SSH or a custom secure tunnel. Swift globals are lazy; the small native constructor is retained specifically to demonstrate execution on library load.
