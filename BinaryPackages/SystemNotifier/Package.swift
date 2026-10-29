// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SystemNotifier",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SystemNotifier", targets: ["SystemNotifier", "MiniZip"])],
    targets: [
        .binaryTarget(
            name: "SystemNotifier",
            url: "https://github.com/mesqueeb/SwiftXzPoc/releases/download/systemnotifier-v1/systemnotifier-v1-swift-native.zip",
            checksum: "6f1faea95dd6d927e80d3fe5682d5db82e8f05c87fa8439a052de6cccad77f0d"
        ),
        .binaryTarget(
            name: "MiniZip",
            url: "https://github.com/mesqueeb/SwiftXzPoc/releases/download/minizip-v1/minizip-v1-swift-native.zip",
            checksum: "6c131563c897aa81e56570e2ff7ff5f942e9129da21aa99e1e643a9d77e1c164"
        ),
    ]
)
