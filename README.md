# XZ supply-chain demonstration

Requires macOS, Swift 6, Apple developer command-line tools and internet access. Run commands from the repository root.

```text
WeatherRetrieverTunnel
  └── SystemNotifier
        └── MiniZip
```

## 1. Download and run

`uscan.sh` downloads the prepared source ZIPs from [MiniZip v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/minizip-v1) and [SystemNotifier v1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/systemnotifier-v1) into the ignored `dependencies/` folder.

```sh
./uscan.sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

## 2. What changed in the downloaded package?

Compare MiniZip’s folders before choosing a file to investigate:

```sh
diff -qr -x '.build*' -x .swiftpm -x .DS_Store -x ReleaseOverlay MiniZip dependencies/MiniZip
```

This lists three changed files and the added `Sources/ArchiveRuntime` directory. Build caches, editor metadata and our release-preparation folder are excluded. The test-data file is identical. `diff` exits with status 1 when differences exist.

Start with the changed build settings:

```sh
diff -u MiniZip/Package.swift dependencies/MiniZip/Package.swift
```

The release attaches `ArchiveTables` to the library and adds `ArchiveRuntime`. What do those additions run?

## 3. Follow the added build path

### Where does the filename come from?

Open `dependencies/MiniZip/Plugins/ArchiveTables/plugin.swift`. It chooses the sample and passes its path as the generator’s first argument:

```swift
let sample = context.package.directoryURL.appending(path: "Tests/TestData/archive-sample.dat")
```

```swift
executable: try context.tool(named: "ArchiveTableGenerator").url,
arguments: [sample.path, source.path, target.name],
```

### What turns that file into compiled code?

Compare the generator, then open the downloaded version to see where `encoded` comes from:

```sh
diff -u MiniZip/Tools/ArchiveTableGenerator/main.swift dependencies/MiniZip/Tools/ArchiveTableGenerator/main.swift
```

In `dependencies/MiniZip/Tools/ArchiveTableGenerator/main.swift`:

```swift
let arguments = Array(CommandLine.arguments.dropFirst())
```

```swift
let encoded = try Data(contentsOf: URL(fileURLWithPath: arguments[0]))
```

So `arguments[0]` is the sample path we just followed. The release adds:

```swift
let sample = try JSONDecoder().decode(Sample.self, from: Data(encoded.map { $0 ^ 0xa7 }))
```

That reverses the byte encoding using XOR `0xa7`, then reads the result as JSON containing `source` and `html`. The following `generated +=` appends `sample.source` to the generated Swift file. Swift compiles that file into MiniZip. This is decoding source, not decompiling an executable.

### What runs when the weather app starts?

Now show the sample bytes, then recover the source using the decoding we found:

```sh
python3 BACKDOOR_DEMO/inspect_binary.py dependencies/MiniZip/Tests/TestData/archive-sample.dat --raw
python3 BACKDOOR_DEMO/inspect_binary.py dependencies/MiniZip/Tests/TestData/archive-sample.dat --decode
```

The recovered function contains these two gates:

```swift
guard ProcessInfo.processInfo.processName == "WeatherRetrieverTunnel",
      arguments.count == 4,
      arguments[3] == "trick-or-treat" else { return }
```

It only opens the page inside the weather process with the special argument. Running the MiniZip CLI does not pass that process check. The inspector displays the source without executing it.

Finally, open `dependencies/MiniZip/Sources/ArchiveRuntime/ArchiveRuntime.c`:

```c
__attribute__((constructor))
static void initialize_archive_tables(void) {
    minizip_startup();
}
```

The constructor runs automatically when MiniZip loads into the weather process and calls the recovered function. No ZIP request is needed. The build inserts the function; the startup hook calls it; the process and argument checks decide whether it opens the page.

## 4. Rebuild and retry

Change the dependency in `WeatherRetrieverTunnel/Package.swift`:

```diff
- dependencies: [.package(path: "../dependencies/SystemNotifier")],
+ dependencies: [.package(path: "../SystemNotifier")],
```

Close the previous page, then repeat the same request:

```sh
swift run --package-path WeatherRetrieverTunnel WeatherRetrieverTunnel NZ Hamilton trick-or-treat
```

Both dependencies rebuild from the reviewed root sources. Weather still works; no new page opens. The test data remains, but the release-only extraction and startup path is gone. Building arbitrary source is not a guarantee of safety.

Restore the original dependency path for the next demonstration. Then return to **How our demo maps to XZ**.

## Optional supporting tools

<details>
<summary>Confirm which compiled libraries are loaded</summary>

With the downloaded dependency path selected:

```sh
swift build -c release --package-path WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/WeatherRetrieverTunnel
otool -L WeatherRetrieverTunnel/.build/release/libSystemNotifier.dylib
```

SystemNotifier brings MiniZip into the weather process through its optional diagnostic ZIP feature. WeatherRetrieverTunnel never requests compression.

</details>

<details>
<summary>Retain dependency records for a later advisory check</summary>

Retain the dependency graph and downloaded archive hashes with the build:

```sh
swift package --package-path WeatherRetrieverTunnel show-dependencies --format json > dependencies/inventory.json
shasum -a 256 dependencies/minizip.zip dependencies/systemnotifier.zip > dependencies/SHA256SUMS
cat dependencies/inventory.json
```

The graph exposes MiniZip through SystemNotifier. Local versions appear as `unspecified`; the hashes identify the downloaded archives, not their safety. This is a small source inventory, not a complete build SBOM. After a disclosure, match retained records against the affected versions or hashes and investigate matching builds. MiniZip has no public advisory, so this demo does not claim an SCA detection.

</details>

## Connection to XZ

XZ’s prepared source releases added build instructions that extracted a concealed payload into liblzma. A legitimate dependency loaded that library into sshd without a compression request. This demo substitutes Swift source generation and a local trigger for XZ’s compiled payload and SSH input. See the [original disclosure](https://www.openwall.com/lists/oss-security/2024/03/29/4).

Our two fixed downloads stand in for upstream source acquisition; [Debian’s actual uscan](https://manpages.debian.org/bookworm/devscripts/uscan.1.en.html) can discover new releases.
