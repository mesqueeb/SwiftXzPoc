// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "WeatherRetrieverTunnel",
    platforms: [.macOS(.v13)],
    products: [.executable(name: "WeatherRetrieverTunnel", targets: ["WeatherRetrieverTunnel"])],
    dependencies: [.package(path: "../BinaryPackages/SystemNotifier")],
    targets: [.executableTarget(name: "WeatherRetrieverTunnel", dependencies: [.product(name: "SystemNotifier", package: "SystemNotifier")], linkerSettings: [.unsafeFlags(["-Xlinker", "-dead_strip_dylibs", "-Xlinker", "-rpath", "-Xlinker", "@executable_path"])])]
)
