// swift-tools-version: 6.0
import PackageDescription
import Foundation

let checksumDirectory = URL(fileURLWithPath: #filePath)
    .deletingLastPathComponent().appendingPathComponent(".build/checksums").path

let package = Package(
    name: "MiniZip",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "MiniZip", type: .dynamic, targets: ["MiniZip"]),
        .executable(name: "minizip", targets: ["MiniZipCLI"])
    ],
    targets: [
        .target(name: "MiniZip", dependencies: ["ArchiveChecksums"], linkerSettings: [.unsafeFlags(["-L", checksumDirectory])]),
        .systemLibrary(name: "ArchiveChecksums"),
        .executableTarget(name: "MiniZipCLI", dependencies: ["MiniZip"]),
        .testTarget(name: "MiniZipTests", dependencies: ["MiniZip"], path: "Tests/MiniZipTests")
    ]
)
