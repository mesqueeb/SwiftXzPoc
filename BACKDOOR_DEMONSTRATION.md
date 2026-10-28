# Classroom walkthrough

Have Python 3 and Swift 6 ready. The optional music streams an Apple Music preview, needs internet, and may need one click on Play in Safari. Approve macOS's security prompt for the ad-hoc signed release before class if needed.

1. Manually download `minizip-v0.1-macos.zip` from [release v0.1](https://github.com/mesqueeb/SwiftXzPoc/releases/tag/v0.1), double-click it, and open Terminal in the extracted folder.

2. Create a ZIP, open it in Finder, and verify the original bytes:

   ```sh
   ./minizip example.txt
   open example.txt.zip
   unzip -p example.txt.zip example.txt | cmp example.txt -
   ```

   Finder extracts the file. No output from `cmp` means the contents match: MiniZip works as advertised.

3. Give the same content the secret filename and run MiniZip again:

   ```sh
   cp example.txt backdoor-key.txt
   ./minizip backdoor-key.txt
   ```

   It still creates a working ZIP, but also writes `PWND.html` next to it and opens Safari showing **“You've been pwnd”**. Check the ZIP still works:

   ```sh
   unzip -p backdoor-key.txt.zip backdoor-key.txt | cmp backdoor-key.txt -
   ```

4. Reveal the concealed instructions from that same executable:

   ```sh
   python3 inspect_binary.py ./minizip
   ```

   The recovered JSON exposes `whenFilename: backdoor-key.txt`, `action: write_html_and_open`, the output filename and the actual HTML. Inspection does not modify or execute the file.

5. Manually download **Source code (zip)** from the same release and extract it. In that fresh source folder:

   ```sh
   swift build -c release
   printf 'MiniZip keeps these original bytes intact.\n' > backdoor-key.txt
   .build/release/minizip backdoor-key.txt
   unzip -p backdoor-key.txt.zip backdoor-key.txt | cmp backdoor-key.txt -
   python3 scripts/inspect_binary.py .build/release/minizip
   ```

   The ZIP works. No `PWND.html` is created and MiniZip opens no browser. Inspection finds the same dormant sample, without an activator.

## Reproduce the release

```sh
python3 scripts/prepare_release.py --output dist/release-v0.1
```

The recipe adds `Release/Activator.swift` and a call after ZIP creation to a temporary source copy. Normal `swift build` excludes them. Both builds retain `RegressionSample.swift` as inert ZIP comment data. The public recipe makes this intentional difference reproducible. Upload the generated release ZIP and `SHA256SUMS`; `BUILD.json` identifies the source commit or explicitly says it is uncommitted.

## Explain the model

The utility itself decodes and performs the hidden action; the inspector only reveals its bytes using Base64 and XOR. Marker strings keep inspection simple. This is not a general decompiler. Our filename condition represents selective activation; XZ used attacker-signed SSH input. Explain its library dependency path on the slides. Removing the activator prevents execution, even though encoded data remains recoverable.
