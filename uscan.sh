#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p dependencies

# A small stand-in for upstream source acquisition, not Debian's actual uscan.
curl -fL https://github.com/mesqueeb/SwiftXzPoc/releases/download/minizip-v1/minizip-v1-swiftpm-source.zip -o dependencies/minizip.zip
curl -fL https://github.com/mesqueeb/SwiftXzPoc/releases/download/systemnotifier-v1/systemnotifier-v1-swiftpm-source.zip -o dependencies/systemnotifier.zip

# Keep the previous sources so a rehearsal can be repeated or reviewed.
previous="$(mktemp -d ./dependencies.before-XXXXXXXX)"
mv dependencies "$previous/sources"
mkdir dependencies
cp "$previous/sources/minizip.zip" dependencies/minizip.zip
cp "$previous/sources/systemnotifier.zip" dependencies/systemnotifier.zip
unzip -q dependencies/minizip.zip -d dependencies
unzip -q dependencies/systemnotifier.zip -d dependencies
