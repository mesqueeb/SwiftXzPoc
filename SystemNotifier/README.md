# SystemNotifier

A normal Swift source package for readiness reporting and optional diagnostic ZIP export. Its `Package.swift` builds `Sources/SystemNotifier` and depends on the sibling MiniZip source package. It does not download its own compiled implementation.

```swift
import SystemNotifier

SystemNotifier.notifyReady()
try SystemNotifier.exportDiagnostics(input: inputURL, output: outputURL)
```

From this folder, `swift build -c release` builds both source packages. Their APIs are Swift; no public C header or `CSystemNotifier` adapter is required.

## Binary distribution

The separate `BinaryPackages/SystemNotifier/Package.swift` declares the downloaded compiled frameworks. WeatherRetrieverTunnel uses that package by default. This makes the choice between source and binary consumption explicit.

The standalone framework builder can rebuild only SystemNotifier against a selected compiled MiniZip framework:

```sh
python3 scripts/build_component.py systemnotifier --source SystemNotifier --minizip PATH_TO_MINIZIP_FRAMEWORK --output dist/notifier-rebuilt
```

This is intentionally different from `swift build` here, which rebuilds MiniZip from its sibling source package too. Rebuilding only the immediate framework retains whatever MiniZip implementation you selected.
