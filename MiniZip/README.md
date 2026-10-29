# MiniZip

A normal Swift source package providing a ZIP library and an optional CLI. `Package.swift` builds its own sources and downloads no compiled implementation.

```swift
import Foundation
import MiniZip

try MiniZip.archive(input: inputURL, output: outputURL)
```

From this folder:

```sh
swift build -c release
swift run minizip example.txt
```

The ZIP storage method preserves the original bytes without reducing size. It supports ordinary files, including spaces and Unicode names, but not directories or ZIP64. Existing output ZIPs are replaced.

## Source and binary builds

The monorepo’s `BinaryPackages/SystemNotifier` package separately describes consumption of published compiled Swift frameworks. It does not change how this source package builds.

The standalone release builder produces `frameworks/MiniZip.framework` with a native Swift interface and `bin/minizip`:

```sh
python3 scripts/build_component.py minizip --source MiniZip --output dist/minizip-reviewed
```

That command runs from the monorepo root. From an extracted prepared source release, use its included `build.py` with `--source .` and a new output folder. The prepared release enables an additional constructor extraction step in that release-builder workflow. The ordinary repository configuration disables it. Plain `swift build` uses the ordinary SwiftPM targets; it does not run the standalone release builder. The walkthrough explicitly uses the release builder when reproducing poisoned release artifacts.

The only native C in the current demonstration is the concealed startup initializer recovered from test data and compiled during that prepared release build. The library API and CLI are Swift. Full explanation is in the monorepo’s `BACKDOOR_DEMO/README.md`.
