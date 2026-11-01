#!/usr/bin/env python3
"""Reassemble ARCHIUM v6.51 from GitHub-friendly text parts, verify SHA-256."""
import hashlib, json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/"release-parts"/"manifest.json").read_text(encoding="utf-8"))
if manifest["version"]!="6.51": sys.exit("Unexpected manifest version")
data=b"".join((root/"release-parts"/f"part{i:03d}.txt").read_bytes() for i in range(manifest["count"]))
digest=hashlib.sha256(data).hexdigest()
if len(data)!=manifest["source_bytes"] or digest!=manifest["sha256"]:
    sys.exit(f"Integrity check failed: bytes={len(data)}, sha256={digest}")
dest=root/"dist"/"index.html"
dest.parent.mkdir(exist_ok=True)
dest.write_bytes(data)
print(f"Release verified and written to {dest}: {len(data)} bytes, sha256={digest}")
