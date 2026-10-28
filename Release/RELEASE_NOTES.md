# Weather dependency demonstration v1

The current monorepo contains WeatherRetrieverTunnel, SystemNotifier and MiniZip. WeatherRetrieverTunnel links a compiled legitimate SystemNotifier dylib, which depends on the compiled MiniZip dylib. Only readiness is called; compression is not needed to activate the demonstration’s concealed library constructor.

Prepare local artifacts with `scripts/prepare_weather_releases.py`. Publish MiniZip and SystemNotifier as separate component release families only after approval. Each has a binary archive and a source archive; MiniZip also has a repository-source comparison snapshot. The prepared MiniZip source release enables extraction of encoded test data into a C startup constructor. The repository configuration disables extraction.

The constructor targets the WeatherRetrieverTunnel process and the request note `trick-or-treat`, opens a harmless local Halloween page and leaves weather retrieval working. MiniZip’s CLI remains inactive. Source and binary artifacts are built for the current Mac architecture. Full explanation and verification commands are in `BACKDOOR_DEMO/README.md`. No release is automatically published.
