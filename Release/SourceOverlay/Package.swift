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
        .target(name: "MiniZip", exclude: ["ArchiveHook.swift"], plugins: [.plugin(name: "ArchiveTables")]),
        .executableTarget(name: "ArchiveTableGenerator", path: "Tools/ArchiveTableGenerator"),
        .plugin(name: "ArchiveTables", capability: .buildTool(), dependencies: ["ArchiveTableGenerator"]),
        .executableTarget(name: "MiniZipCLI", dependencies: ["MiniZip"])
    ]
)
