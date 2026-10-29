# SystemNotifier

A macOS notification helper with readiness reporting and optional ZIP export of diagnostic files. Its native shared library is written in Swift and calls MiniZip only for diagnostic ZIP creation. Its small Swift package interface lets WeatherRetrieverTunnel use the downloaded compiled library.

The weather app only calls `SystemNotifier.notifyReady()`. The native `libSystemNotifier.dylib` has a load dependency on `libMiniZip.dylib`, even when the optional diagnostic function is unused.

The default package build automatically fetches both SystemNotifier and MiniZip from their v1 releases and verifies both archive checksums. A network connection is needed for the first build; subsequent builds can reuse SwiftPM’s cache. No `Downloads/` folder is required. The local package provides the Swift interface but does not compile `Native/Notifier.swift` automatically. To rebuild that native library yourself, use a new output folder:

```sh
python3 scripts/build_component.py systemnotifier --source SystemNotifier --minizip WeatherRetrieverTunnel/.build/artifacts/systemnotifier/MiniZip/MiniZip.xcframework/macos-arm64 --output dist/notifier-rebuilt
```

This rebuild still uses the selected compiled MiniZip. To remove this demonstration’s extra code, rebuild MiniZip from the reviewed repository version as well. See `BACKDOOR_DEMO/README.md` in the monorepo.

The example above uses the fetched Apple Silicon MiniZip XCFramework slice. For the comparison, copy the rebuilt dylib beside the weather executable, replacing `WeatherRetrieverTunnel/.build/release/libSystemNotifier.dylib`. Run the built executable directly afterward. For the reviewed-source comparison, replace `WeatherRetrieverTunnel/.build/release/libMiniZip.dylib` with the reviewed build. This changes the runtime copy without modifying the cached XCFramework; a later build may restore the pinned library. The standalone MiniZip CLI archive remains optional.
