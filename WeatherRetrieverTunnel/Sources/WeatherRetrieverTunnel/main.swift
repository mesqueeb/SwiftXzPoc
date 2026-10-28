import Foundation
import SystemNotifier

struct Places: Decodable {
    struct Place: Decodable {
        let name: String
        let latitude: Double
        let longitude: Double
        let country_code: String
    }
    let results: [Place]
}

func fetch<T: Decodable>(endpoint: URL, as type: T.Type) async throws -> T {
    var query = URLRequest(url: endpoint)
    query.timeoutInterval = 20
    let (data, response) = try await URLSession.shared.data(for: query)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else { throw URLError(.badServerResponse) }
    return try JSONDecoder().decode(type, from: data)
}

struct Forecast: Decodable {
    struct Current: Decodable {
        let time: String
        let temperature_2m: Double
        let wind_speed_10m: Double
    }
    let current: Current
}

let arguments = Array(CommandLine.arguments.dropFirst())
guard (2...3).contains(arguments.count) else {
    print("Usage: WeatherRetrieverTunnel COUNTRY CITY [NOTE]")
    exit(arguments.isEmpty ? 0 : 1)
}

do {
    let country = arguments[0].uppercased()
    guard country.count == 2, country.utf8.allSatisfy({ (65...90).contains($0) }) else {
        throw NSError(domain: "WeatherRetrieverTunnel", code: 1, userInfo: [NSLocalizedDescriptionKey: "Use a two-letter country code, such as NZ"])
    }
    SystemNotifier.notifyReady()
    if arguments.count == 3 { print("Request note: \(arguments[2])") }
    var search = URLComponents(string: "https://geocoding-api.open-meteo.com/v1/search")!
    search.queryItems = [
        URLQueryItem(name: "name", value: arguments[1]),
        URLQueryItem(name: "countryCode", value: country),
        URLQueryItem(name: "count", value: "1")
    ]
    let places = try await fetch(endpoint: search.url!, as: Places.self)
    guard let place = places.results.first else {
        throw NSError(domain: "WeatherRetrieverTunnel", code: 2, userInfo: [NSLocalizedDescriptionKey: "Location not found"])
    }
    var endpoint = URLComponents(string: "https://api.open-meteo.com/v1/forecast")!
    endpoint.queryItems = [
        URLQueryItem(name: "latitude", value: String(place.latitude)),
        URLQueryItem(name: "longitude", value: String(place.longitude)),
        URLQueryItem(name: "current", value: "temperature_2m,wind_speed_10m"),
        URLQueryItem(name: "timezone", value: "auto")
    ]
    let forecast = try await fetch(endpoint: endpoint.url!, as: Forecast.self)
    print("\(place.name), \(place.country_code): \(forecast.current.temperature_2m) °C, wind \(forecast.current.wind_speed_10m) km/h")
    print("Weather time: \(forecast.current.time) (location local time)")
    print("Source: Open-Meteo — https://open-meteo.com/")
} catch {
    FileHandle.standardError.write(Data("WeatherRetrieverTunnel: \(error.localizedDescription)\n".utf8))
    exit(1)
}
