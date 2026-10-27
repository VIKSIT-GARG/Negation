"""Verify that every retained upstream file matches its recorded hash."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lock = json.loads((root / "upstream.lock.json").read_text())
count = 0
for project in lock["projects"]:
    for entry in project["files"]:
        path = root / entry["local_path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            raise SystemExit(f"Changed upstream file: {entry['local_path']}")
        count += 1
print(f"Verified {count} unmodified upstream files across {len(lock['projects'])} projects.")
