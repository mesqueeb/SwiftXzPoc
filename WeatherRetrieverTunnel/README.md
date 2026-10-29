# WeatherRetrieverTunnel

Fetch current weather for a city and country:

```sh
swift build -c release
.build/release/WeatherRetrieverTunnel NZ hamilton
.build/release/WeatherRetrieverTunnel NZ hamilton "a request note"
```

Use a two-letter country code and quote city names containing spaces. Output includes the resolved location, temperature, wind speed and weather timestamp. The optional note is printed locally and is not sent to the weather provider.

The app uses SystemNotifier to report readiness. Its default manifest points to `../BinaryPackages/SystemNotifier`, which fetches two compiled Swift frameworks. The implementation source is separately available in `../SystemNotifier`. No manual artifact installation is needed; the first build needs internet. The app does not import MiniZip or call any ZIP function.

Weather and place lookup use [Open-Meteo](https://open-meteo.com/en/docs) and its [geocoding API](https://open-meteo.com/en/docs/geocoding-api), based on GeoNames. Internet access is required; errors are reported rather than replaced with invented weather. “Tunnel” is the example’s name: it is an HTTPS weather client, not an SSH server or custom encrypted tunnel.

## Build from the source packages

From the repository root, run `python3 scripts/select_weather_dependency.py source` to select the manifest pointing to the real SystemNotifier source package. It builds MiniZip from source too. Use a separate scratch directory when switching between source and binary builds. Select `binary` to return to downloaded frameworks. The checked-in manifest examples make the choice visible.
