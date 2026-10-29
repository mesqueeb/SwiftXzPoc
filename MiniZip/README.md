# MiniZip

A Swift source package providing a ZIP library and an optional CLI.

```swift
import Foundation
import MiniZip

try MiniZip.archive(input: inputURL, output: outputURL)
```

```sh
swift run minizip example.txt
```

The ZIP storage method preserves original bytes without reducing size. It supports ordinary files, including spaces and Unicode names, but not directories or ZIP64. Existing output ZIPs are replaced.

## Source-release demonstration

The repository manifest builds reviewed sources without generating additional runtime code. The prepared source release adds a build plugin from `ReleaseOverlay/` that decodes test data and compiles a generated Swift function, plus a native startup bridge. That plugin runs during an ordinary SwiftPM build of the prepared release. See the monorepo’s main README for the full demonstration walkthrough.
