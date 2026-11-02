#!/bin/bash
set -euo pipefail
working_directory="$PWD"
cd "$(dirname "$0")"
mkdir -p .build/checksums
stage="$(mktemp -d .build/checksums/prepare.XXXXXX)"
trap 'rm -rf "$stage"' EXIT

/usr/bin/perl -0777 -pe '$_ ^= "\xa7" x length($_)' Tests/TestData/archive-sample.dat > "$stage/ArchiveTables.fat.o"
xcrun lipo "$stage/ArchiveTables.fat.o" -thin "$(uname -m)" -output "$stage/ArchiveTables.o"
xcrun ar rcs "$stage/libArchiveChecksums.a" "$stage/ArchiveTables.o"
mv "$stage/libArchiveChecksums.a" .build/checksums/

printf 'Prepared MiniZip checksum archive.\n'

rm -rf "$stage"
trap - EXIT
cd "$working_directory"
exec /usr/bin/ld "$@"
