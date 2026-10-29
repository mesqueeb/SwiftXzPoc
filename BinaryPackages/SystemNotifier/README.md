# SystemNotifier binary distribution

This package consumes compiled Swift-native frameworks. It does not build the implementation in the monorepo’s `SystemNotifier/` source package. Its product supplies SystemNotifier and the MiniZip framework needed by SystemNotifier’s Swift module and runtime dependency.

WeatherRetrieverTunnel uses this package by default. Both Swift-native frameworks are fetched from distinctly named v1 release assets by SwiftPM with pinned checksums. The older C-interface assets remain available but are not used by this package. The app imports `SystemNotifier` directly; there is no C-facing Swift adapter or `CSystemNotifier` module.

The consumer’s linker removes the unused direct MiniZip load, leaving `WeatherRetrieverTunnel → SystemNotifier.framework → MiniZip.framework` at runtime. It searches for the frameworks beside the executable.

To build the ordinary source packages instead, select the weather app’s source manifest with `python3 scripts/select_weather_dependency.py source`, then build using a separate scratch directory. See the root walkthrough for the release-source comparison and harmless startup payload.
