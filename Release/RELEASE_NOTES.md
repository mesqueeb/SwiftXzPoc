# MiniZip v0.1

Create a ZIP from one file with `./minizip example.txt`. Supports Apple Silicon and Intel Macs, macOS 13 or later. Files are stored without compression.

Download `minizip-v0.1-macos.zip`, extract it, and follow `BACKDOOR_DEMONSTRATION.md` for the classroom walkthrough. The bundle includes the executable, inspector and example file. The executable is ad-hoc signed rather than notarised.

This teaching release intentionally adds the activator described in `Release/Activator.swift`; a normal repository source build omits it. `BUILD.json` records the source revision and executable hash. Attach the release ZIP and `SHA256SUMS` to tag `v0.1` at the reviewed source revision.
