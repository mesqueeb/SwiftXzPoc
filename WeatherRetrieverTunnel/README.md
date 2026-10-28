# WeatherRetrieverTunnel

Fetch current weather for a city and country:

```sh
swift build -c release
.build/release/WeatherRetrieverTunnel NZ hamilton
.build/release/WeatherRetrieverTunnel NZ hamilton "a request note"
```

Use a two-letter country code and quote city names containing spaces. Output includes the resolved location, temperature, wind speed and weather timestamp. The optional note is printed locally and is not sent to the weather provider.

The app uses SystemNotifier to report readiness. Its package manifest references the sibling SystemNotifier package, whose interface links downloaded compiled libraries. Follow the monorepo README to install those artifacts first. The app does not import MiniZip or call any ZIP function.

Weather and place lookup use [Open-Meteo](https://open-meteo.com/en/docs) and its [geocoding API](https://open-meteo.com/en/docs/geocoding-api), based on GeoNames. Internet access is required; errors are reported rather than replaced with invented weather. “Tunnel” is the example’s name: it is an HTTPS weather client, not an SSH server or custom encrypted tunnel.
