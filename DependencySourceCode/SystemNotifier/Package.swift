// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SystemNotifier",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SystemNotifier", type: .dynamic, targets: ["SystemNotifier"])],
    dependencies: [.package(path: "../MiniZip")],
    targets: [.target(
        name: "SystemNotifier",
        dependencies: [.product(name: "MiniZip", package: "MiniZip")]
    )]
)
