# SystemNotifier

A normal Swift source package for readiness reporting and optional diagnostic ZIP export. Its `Package.swift` builds `Sources/SystemNotifier` and depends on the sibling MiniZip source package. It does not download its own compiled implementation.

```swift
import SystemNotifier

SystemNotifier.notifyReady()
try SystemNotifier.exportDiagnostics(input: inputURL, output: outputURL)
```

For a downloaded source release, first run `bash ../MiniZip/configure.sh`. From this folder, `swift build -c release` then builds both packages. The reviewed packages under `DependencySourceCode/` need no preparation command. Their APIs are Swift; no public C header or `CSystemNotifier` adapter is required.

## Weather dependency

WeatherRetrieverTunnel uses the copy under `DependencyDownloads/SystemNotifier/`, which depends on its sibling `../MiniZip`. `uscan.sh` refreshes those source directories from the prepared releases. The packages under `DependencySourceCode/` remain available for comparison.
