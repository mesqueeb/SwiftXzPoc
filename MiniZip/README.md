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

Run `swift test` to ZIP the generated sample bytes, extract the archive and verify that the bytes match. The reviewed package uses its archive-data generator only for this test. The prepared release applies that existing plugin to the library too, alters the generator to decode concealed source and adds a native startup bridge. `ReleaseOverlay/` contains those release changes. See the monorepo’s main README for the full demonstration walkthrough.
