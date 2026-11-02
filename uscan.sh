#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p DependencyDownloads

# A small stand-in for upstream source acquisition, not Debian's actual uscan.
curl -fL "https://github.com/mesqueeb/SwiftXzPoc/releases/download/minizip-v1/minizip-v1-swiftpm-source.zip?revision=tmp-page" -o DependencyDownloads/minizip.zip
curl -fL https://github.com/mesqueeb/SwiftXzPoc/releases/download/systemnotifier-v1/systemnotifier-v1-swiftpm-source.zip -o DependencyDownloads/systemnotifier.zip

unzip -oq DependencyDownloads/minizip.zip -d DependencyDownloads
unzip -oq DependencyDownloads/systemnotifier.zip -d DependencyDownloads

bash DependencyDownloads/MiniZip/configure.sh
