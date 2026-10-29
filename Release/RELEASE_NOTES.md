# Swift-native source and binary separation

The normal source packages are `MiniZip/` and `SystemNotifier/`. Their manifests build their own Swift implementations, with SystemNotifier depending on the sibling MiniZip source. Neither downloads its own implementation.

`BinaryPackages/SystemNotifier/` is the separate compiled-distribution manifest used by WeatherRetrieverTunnel by default. It fetches Swift-native SystemNotifier and MiniZip XCFrameworks. The older v1 C-interface assets are preserved; the new artifact names contain `swift-native` and expose normal Swift APIs.

The only C required by the active demonstration is the concealed library constructor. The standalone prepared-release builder extracts and compiles it from test data. Plain SwiftPM source builds use the ordinary reviewed targets and stay inactive. The walkthrough explicitly distinguishes those two build workflows.

Select `source` or `binary` with `scripts/select_weather_dependency.py`, then use a separate build directory. Tests cover both paths, framework replacement comparisons, CLI extraction and the indirect runtime dependency chain. Source changes remain uncommitted until requested.
