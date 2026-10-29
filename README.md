# WeatherRetrieverTunnel, SystemNotifier and MiniZip

A small macOS weather client, a notification helper and a ZIP library.

```sh
cd WeatherRetrieverTunnel
swift run WeatherRetrieverTunnel NZ Hamilton
```

The default build automatically fetches compiled Swift-native frameworks through the separate `BinaryPackages/SystemNotifier` package. No manual downloads are required. Weather lookup uses Open-Meteo and GeoNames and needs internet. The optional third argument is a request note.

## Source packages and binary distribution

```text
MiniZip/                       ordinary Swift source package
SystemNotifier/                ordinary Swift source package; depends on ../MiniZip
BinaryPackages/SystemNotifier/ compiled framework distribution manifest
WeatherRetrieverTunnel/        app; defaults to the binary-distribution package
```

Both source manifests build their own Swift implementations. Neither source package downloads itself. SystemNotifier uses MiniZip only for optional diagnostic ZIP creation; the weather app calls readiness reporting only.

Choose explicitly from the repository root:

```sh
python3 scripts/select_weather_dependency.py source
swift run --package-path WeatherRetrieverTunnel --scratch-path .build-source WeatherRetrieverTunnel NZ Hamilton
```

Return to the compiled distribution:

```sh
python3 scripts/select_weather_dependency.py binary
swift run --package-path WeatherRetrieverTunnel --scratch-path .build-binary WeatherRetrieverTunnel NZ Hamilton
```

The selector changes the weather manifest to one of the checked-in examples under `WeatherRetrieverTunnel/Manifests/`. Use separate build directories to make the comparison clear.

Swift 6 and Apple developer command-line tools are required. The prepared frameworks target macOS 13 or later and the Mac architecture recorded in their build metadata. The native Swift framework builder ships module interfaces; the ordinary source packages can also be built directly with SwiftPM.

## Demonstration

This is a harmless model of the XZ supply-chain incident. A prepared MiniZip release build incorporates concealed C startup code from test data into its Swift framework. The ordinary source build does not. See [BACKDOOR_DEMO/README.md](BACKDOOR_DEMO/README.md) for the trigger, extraction, source comparison and differences from XZ.

Earlier root-package and backup-demo files remain historical and are not used by the weather packages.
