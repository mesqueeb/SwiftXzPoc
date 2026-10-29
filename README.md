# WeatherRetrieverTunnel, SystemNotifier and MiniZip

A small macOS weather client with a notification helper and a ZIP library. Fetch weather for a city from your terminal:

```sh
WeatherRetrieverTunnel NZ hamilton
```

## Build the weather app

Clone this repository, then run:

```sh
cd WeatherRetrieverTunnel
swift run WeatherRetrieverTunnel NZ Hamilton
```

SwiftPM automatically downloads the pinned SystemNotifier and MiniZip XCFrameworks from their v1 releases and verifies both SHA-256 checksums. No manual downloads or `Downloads/` folder are needed for normal use. The standalone binary ZIPs remain available for running MiniZip separately or demonstrating local library overrides.

Swift 6 and Apple developer command-line tools are required. Weather lookup needs internet and uses Open-Meteo and GeoNames. The executable accepts an optional third argument as a request note. The release libraries are built for macOS 13 or later and the architecture identified in their build records.

`WeatherRetrieverTunnel/Package.swift` depends on the sibling SystemNotifier package. That small interface declares both compiled libraries as remote binary targets. SystemNotifier loads the SwiftPM-fetched MiniZip library at runtime. The source trees being present does not automatically rebuild those native libraries. See each component’s README for source build instructions.

SystemNotifier supports readiness reporting and optional compressed diagnostics. MiniZip provides a single-file ZIP library and a standalone CLI; its ZIP storage method preserves bytes without reducing file size. Existing output ZIPs are replaced, and directories and ZIP64 are unsupported.

## Demonstration

This repository is a harmless model of the XZ Utils supply-chain backdoor. The prepared MiniZip source release adds an extraction build step that incorporates concealed startup code into its compiled library. See [BACKDOOR_DEMO/README.md](BACKDOOR_DEMO/README.md) for the manual walkthrough, inspection and repository-source comparison. Nothing is automatically published by the build scripts.

The old root Swift package and backup-demo files are retained as earlier versions. Use the component folders above for the current weather demonstration.
