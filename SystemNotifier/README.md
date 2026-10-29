# SystemNotifier

A normal Swift source package for readiness reporting and optional diagnostic ZIP export. Its `Package.swift` builds `Sources/SystemNotifier` and depends on the sibling MiniZip source package. It does not download its own compiled implementation.

```swift
import SystemNotifier

SystemNotifier.notifyReady()
try SystemNotifier.exportDiagnostics(input: inputURL, output: outputURL)
```

From this folder, `swift build -c release` builds both source packages. Their APIs are Swift; no public C header or `CSystemNotifier` adapter is required.

## Weather dependency

WeatherRetrieverTunnel uses the copy under `dependencies/SystemNotifier/`, which depends on its sibling `../MiniZip`. `uscan.sh` refreshes those source directories from the prepared releases. The root project source remains available for comparison.
