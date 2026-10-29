#!/usr/bin/env python3
"""Select an explicit source or binary dependency manifest for the weather app."""

import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=["binary", "source"])
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
weather = root / "WeatherRetrieverTunnel"
selected = weather / "Manifests" / f"Package.{args.mode}.swift"
(weather / "Package.swift").write_text(selected.read_text())
print(f"WeatherRetrieverTunnel now uses the {args.mode} package. Use a separate scratch path when switching modes.")
