// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "MiniZip",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "MiniZip", targets: ["MiniZip"]),
        .executable(name: "minizip", targets: ["MiniZipCLI"])
    ],
    targets: [
        .target(name: "MiniZip"),
        .executableTarget(name: "MiniZipCLI", dependencies: ["MiniZip"])
    ]
)
