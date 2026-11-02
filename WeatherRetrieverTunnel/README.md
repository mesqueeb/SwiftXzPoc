# WeatherRetrieverTunnel

First run `./uscan.sh` from the repository root to download the dependencies. Then, from this folder, fetch current weather for a city and country:

```sh
swift build -c release
.build/release/WeatherRetrieverTunnel NZ hamilton
.build/release/WeatherRetrieverTunnel NZ hamilton "a request note"
```

Use a two-letter country code and quote city names containing spaces. Output includes the resolved location, temperature, wind speed and weather timestamp. The optional note is printed locally and is not sent to the weather provider.

The app uses `../DependencyDownloads/SystemNotifier` to report readiness. That package depends on its sibling MiniZip source package. SwiftPM builds the packages locally. The app does not import MiniZip or call any ZIP function.

Weather and place lookup use [Open-Meteo](https://open-meteo.com/en/docs) and its [geocoding API](https://open-meteo.com/en/docs/geocoding-api), based on GeoNames. Internet access is required; errors are reported rather than replaced with invented weather. “Tunnel” is the example’s name: it is an HTTPS weather client, not an SSH server or custom encrypted tunnel.

## Prepared source-release demonstration

Run `./uscan.sh` from the repository root. It only downloads and extracts the source releases. During the SwiftPM build, MiniZip’s release manifest invokes `configure.sh` as a linker wrapper to prepare the checksum archive, then run Apple’s linker. The MiniZip release links a compiled checksum object recovered from test data. Its startup function runs when MiniZip loads into the weather process. The reviewed packages under `DependencySourceCode/` compile the ordinary checksum source instead. See the [main README](../README.md) for the walkthrough.
