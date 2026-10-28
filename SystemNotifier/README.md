# SystemNotifier

A macOS notification helper with readiness reporting and optional ZIP export of diagnostic files. Its native shared library is written in Swift and calls MiniZip only for diagnostic ZIP creation. Its small Swift package interface lets WeatherRetrieverTunnel use the downloaded compiled library.

The weather app only calls `SystemNotifier.notifyReady()`. The native `libSystemNotifier.dylib` has a load dependency on `libMiniZip.dylib`, even when the optional diagnostic function is unused.

The default package build expects only the SystemNotifier binary release extracted into the monorepo’s `Downloads/` folder. SwiftPM fetches MiniZip automatically from its v1 release and verifies the archive checksum. A network connection is needed for the first build; subsequent builds can reuse SwiftPM’s cache. It intentionally does not compile `Native/Notifier.swift` automatically. To rebuild that native library yourself, use a new output folder:

```sh
python3 scripts/build_component.py systemnotifier --source SystemNotifier --minizip WeatherRetrieverTunnel/.build/artifacts/systemnotifier/MiniZip/MiniZip.xcframework/macos-arm64 --output dist/notifier-rebuilt
```

This rebuild still uses the selected compiled MiniZip. To remove this demonstration’s extra code, rebuild MiniZip from the reviewed repository version as well. See `BACKDOOR_DEMO/README.md` in the monorepo.

The example above uses the fetched Apple Silicon XCFramework slice. An explicitly installed `Downloads/MiniZip/lib/libMiniZip.dylib` overrides the cached library through the notifier’s loader search path; the reviewed-source comparison uses this intentionally. The standalone MiniZip CLI archive remains optional.
