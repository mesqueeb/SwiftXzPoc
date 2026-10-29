#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p dependencies

# A small stand-in for upstream source acquisition, not Debian's actual uscan.
curl -fL https://github.com/mesqueeb/SwiftXzPoc/releases/download/minizip-v1/minizip-v1-swiftpm-source.zip -o dependencies/minizip.zip
curl -fL https://github.com/mesqueeb/SwiftXzPoc/releases/download/systemnotifier-v1/systemnotifier-v1-swiftpm-source.zip -o dependencies/systemnotifier.zip

unzip -oq dependencies/minizip.zip -d dependencies
unzip -oq dependencies/systemnotifier.zip -d dependencies
