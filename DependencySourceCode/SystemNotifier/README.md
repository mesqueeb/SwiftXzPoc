# SystemNotifier

A normal Swift source package for readiness reporting and optional diagnostic ZIP export. Its `Package.swift` builds `Sources/SystemNotifier` and depends on the sibling MiniZip source package. It does not download its own compiled implementation.

```swift
import SystemNotifier

SystemNotifier.notifyReady()
try SystemNotifier.exportDiagnostics(input: inputURL, output: outputURL)
```

From this folder, `swift build -c release` builds both packages. In a downloaded source release, MiniZip’s manifest automatically invokes its `configure.sh` linker wrapper during the build. The reviewed packages under `DependencySourceCode/` need no preparation command. Their APIs are Swift; no public C header or `CSystemNotifier` adapter is required.

## Weather dependency

WeatherRetrieverTunnel uses the copy under `DependencyDownloads/SystemNotifier/`, which depends on its sibling `../MiniZip`. `uscan.sh` refreshes those source directories from the prepared releases. The packages under `DependencySourceCode/` remain available for comparison.
