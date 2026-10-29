// swift-tools-version: 6.0
import PackageDescription
let package = Package(
    name: "SystemNotifier",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SystemNotifier", targets: ["SystemNotifier"])],
    targets: [
        .binaryTarget(
            name: "MiniZip",
            url: "https://github.com/mesqueeb/SwiftXzPoc/releases/download/minizip-v1/minizip-v1-swiftpm.zip",
            checksum: "bf3cd3efa6050492e3b645e9d30750ef4f3f3b6ee42130d008f4ba6b18d8fd0b"
        ),
        .binaryTarget(
            name: "CSystemNotifier",
            url: "https://github.com/mesqueeb/SwiftXzPoc/releases/download/systemnotifier-v1/systemnotifier-v1-swiftpm.zip",
            checksum: "40e103ae8b1f12f8025ecd50a08ba1e9f997fc58ee4c61609bc510b32fe9efc4"
        ),
        .target(name: "SystemNotifier", dependencies: ["CSystemNotifier", "MiniZip"], linkerSettings: [.unsafeFlags([
            // Keep MiniZip as SystemNotifier’s runtime dependency rather than a direct app load.
            "-Xlinker", "-dead_strip_dylibs"
        ])])
    ]
)
