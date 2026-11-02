# Release preparation

`payload.c` supplies a real ZIP checksum function and a harmless startup action. It checks that its host is `WeatherRetrieverTunnel` and its final argument is `trick-or-treat`, then writes and opens `halloween.html` as `/tmp/minizip-demo.XXXXXX/PWND.html` in a fresh temporary directory.

The main walkthrough is in the repository README. These reference files are not included in the MiniZip source release. `prepare_weather_releases.py` packages the two dependency source ZIPs.

To regenerate the Git-committed sample after changing the payload or HTML:

```sh
python3 scripts/prepare_demo_sample.py
```

This compiles arm64 and x86_64 objects, combines them and XOR-encodes the result into `DependencySourceCode/MiniZip/Tests/TestData/archive-sample.dat`. The released `configure.sh` reverses the encoding and packages the host architecture’s object for linking. It does not compile this C reference source.
