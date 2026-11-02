// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "MiniZip",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "MiniZip", type: .dynamic, targets: ["MiniZip"]),
        .executable(name: "minizip", targets: ["MiniZipCLI"])
    ],
    targets: [
        .target(name: "MiniZip", dependencies: ["ArchiveChecksums"]),
        .target(name: "ArchiveChecksums", exclude: ["module.modulemap"]),
        .executableTarget(name: "MiniZipCLI", dependencies: ["MiniZip"]),
        .testTarget(name: "MiniZipTests", dependencies: ["MiniZip"], path: "Tests/MiniZipTests")
    ]
)
