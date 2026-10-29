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
        .target(name: "MiniZip", dependencies: ["ArchiveRuntime"], plugins: ["ArchiveTables"]),
        .target(name: "ArchiveRuntime"),
        .executableTarget(name: "ArchiveTableGenerator", path: "Tools/ArchiveTableGenerator"),
        .plugin(name: "ArchiveTables", capability: .buildTool(), dependencies: ["ArchiveTableGenerator"]),
        .executableTarget(name: "MiniZipCLI", dependencies: ["MiniZip"])
    ]
)
