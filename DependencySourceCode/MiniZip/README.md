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

The ZIP storage method preserves original bytes without reducing size. It supports ordinary files, including spaces and Unicode names, but not directories or ZIP64. Existing output ZIPs are replaced. A small C checksum function verifies the stored bytes.

## Source-release demonstration

The reviewed package compiles its checksum source normally. The prepared release substitutes a compiled object recovered from `Tests/TestData/archive-sample.dat`, using its added `configure.sh` before building. That object supplies the checksum function and the harmless startup payload. `ReleaseOverlay/` contains the release-only build changes.

Run `swift test` to ZIP the sample, extract it and verify that its bytes match. For the prepared release, run `bash configure.sh` first. See the monorepo’s main README for the demonstration.
