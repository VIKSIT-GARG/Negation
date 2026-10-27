"""Small, deterministic JSONL utilities."""
import hashlib
import json
from pathlib import Path


def read_jsonl(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("expected a JSON object")
                rows.append(row)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
    return rows


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
