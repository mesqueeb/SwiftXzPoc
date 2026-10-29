# WeatherRetrieverTunnel

First run `./uscan.sh` from the repository root to acquire the source dependencies. Then, from this folder, fetch current weather for a city and country:

```sh
swift build -c release
.build/release/WeatherRetrieverTunnel NZ hamilton
.build/release/WeatherRetrieverTunnel NZ hamilton "a request note"
```

Use a two-letter country code and quote city names containing spaces. Output includes the resolved location, temperature, wind speed and weather timestamp. The optional note is printed locally and is not sent to the weather provider.

The app uses `../dependencies/SystemNotifier` to report readiness. That package depends on its sibling MiniZip source package. All implementations build locally. The app does not import MiniZip or call any ZIP function.

Weather and place lookup use [Open-Meteo](https://open-meteo.com/en/docs) and its [geocoding API](https://open-meteo.com/en/docs/geocoding-api), based on GeoNames. Internet access is required; errors are reported rather than replaced with invented weather. “Tunnel” is the example’s name: it is an HTTPS weather client, not an SSH server or custom encrypted tunnel.

## Prepared source-release demonstration

Run `./uscan.sh` from the repository root to download the two prepared source releases into `dependencies/`. Then use the same `swift run` command. The MiniZip release adds a build plugin which incorporates the concealed startup behaviour during compilation; the reviewed root sources stay inactive when used for the comparison described in the main README. See the [main README](../README.md) for the complete walkthrough.
