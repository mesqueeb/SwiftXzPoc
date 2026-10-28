# MiniZip

A small macOS library that stores an ordinary file in a valid ZIP. It also provides the `minizip FILE` command. Swift 6, Python 3 and Apple command-line developer tools are required to build it. Output targets the current Mac architecture and macOS 13 or later.

From the monorepo root, build the reviewed repository version into a new folder:

```sh
python3 scripts/build_component.py minizip --source MiniZip --output dist/minizip-reviewed
```

From an extracted standalone source archive, use the included script:

```sh
python3 build.py minizip --source . --output ../minizip-built
```

The source release’s build configuration enables extraction of concealed test data into a C library initializer. The repository configuration leaves extraction disabled. Merely rebuilding an arbitrary source release does not remove that difference. See the monorepo’s `BACKDOOR_DEMO/README.md` for the full explanation.
