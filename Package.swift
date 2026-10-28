// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SwiftXzPoc",
    platforms: [.macOS(.v13)],
    products: [.executable(name: "minizip", targets: ["SwiftXzPoc"])],
    targets: [.executableTarget(name: "SwiftXzPoc")]
)
