// swift-tools-version: 6.0
import PackageDescription
import Foundation

let downloads = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("Downloads")
let notifier = downloads.appendingPathComponent("SystemNotifier/lib/libSystemNotifier.dylib")
guard FileManager.default.fileExists(atPath: notifier.path) else {
    fatalError("Missing \(notifier.path). Extract the SystemNotifier binary release into Downloads/. MiniZip is fetched automatically by SwiftPM.")
}
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
        .systemLibrary(name: "CSystemNotifier"),
        .target(name: "SystemNotifier", dependencies: ["CSystemNotifier", "MiniZip"], linkerSettings: [.unsafeFlags([
            // Keep MiniZip as SystemNotifier’s runtime dependency rather than a direct app load.
            "-Xlinker", "-dead_strip_dylibs",
            "-L", downloads.appendingPathComponent("SystemNotifier/lib").path,
            "-Xlinker", "-rpath", "-Xlinker", downloads.appendingPathComponent("SystemNotifier/lib").path,
            "-Xlinker", "-rpath", "-Xlinker", downloads.appendingPathComponent("MiniZip/lib").path
        ])])
    ]
)
