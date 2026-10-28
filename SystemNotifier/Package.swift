// swift-tools-version: 6.0
import PackageDescription
import Foundation

let downloads = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("Downloads")
for component in ["SystemNotifier", "MiniZip"] {
    let binary = downloads.appendingPathComponent("\(component)/lib/lib\(component).dylib")
    guard FileManager.default.fileExists(atPath: binary.path) else {
        fatalError("Missing \(binary.path). Extract the component binary releases into Downloads/. See BACKDOOR_DEMO/README.md.")
    }
}
let package = Package(
    name: "SystemNotifier",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SystemNotifier", targets: ["SystemNotifier"])],
    targets: [
        .systemLibrary(name: "CSystemNotifier"),
        .target(name: "SystemNotifier", dependencies: ["CSystemNotifier"], linkerSettings: [.unsafeFlags([
            "-L", downloads.appendingPathComponent("SystemNotifier/lib").path,
            "-Xlinker", "-rpath", "-Xlinker", downloads.appendingPathComponent("SystemNotifier/lib").path,
            "-Xlinker", "-rpath", "-Xlinker", downloads.appendingPathComponent("MiniZip/lib").path
        ])])
    ]
)
