"""Attach generated media and extract uniformly spaced, auditable frames."""
from pathlib import Path
from .dataset import validate
from .io import file_hash


def attach_media(dataset, manifest):
    known = {r["sample_id"] for r in dataset}
    mapping = {}
    for record in manifest:
        sid = record.get("sample_id")
        if sid not in known or sid in mapping:
            raise ValueError(f"unknown/duplicate media sample: {sid}")
        path = Path(record["media_path"]).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"media file missing: {path}")
        mapping[sid] = {"media_path": str(path), "media_sha256": file_hash(path),
                        "generation": {k: record[k] for k in ("generator", "generator_revision", "seed", "guidance_scale", "steps", "duration_seconds") if k in record}}
    rows = [dict(row, **mapping.get(row["sample_id"], {})) for row in dataset]
    validate(rows)
    return rows


def uniform_indices(total, count):
    if total < 1 or count < 1:
        raise ValueError("total and count must be positive")
    return sorted({round(i * (total - 1) / (count - 1)) for i in range(count)}) if count > 1 else [0]


def extract_frames(dataset, output_dir, count=8):
    import cv2
    validate(dataset)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in dataset:
        if not row.get("media_path"):
            raise ValueError(f"no media attached: {row['sample_id']}")
        source = Path(row["media_path"])
        digest = file_hash(source)
        if row.get("media_sha256") and row["media_sha256"] != digest:
            raise ValueError(f"media changed since attach: {row['sample_id']}")
        capture = cv2.VideoCapture(str(source))
        frames = []
        try:
            if not capture.isOpened():
                raise ValueError(f"cannot open video: {source}")
            total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = capture.get(cv2.CAP_PROP_FPS)
            for index in uniform_indices(total, count):
                capture.set(cv2.CAP_PROP_POS_FRAMES, index)
                ok, frame = capture.read()
                if not ok:
                    raise ValueError(f"cannot decode {source} frame {index}")
                # File names are content hashes; dataset IDs never become paths.
                destination = output_dir / f"{digest}.{index:08d}.jpg"
                if not cv2.imwrite(str(destination), frame):
                    raise OSError(f"cannot write {destination}")
                frames.append({"path": str(destination), "frame_index": index,
                               "time_seconds": index / fps if fps > 0 else None,
                               "sha256": file_hash(destination)})
        finally:
            capture.release()
        rows.append({"sample_id": row["sample_id"], "media_sha256": digest, "frames": frames})
    return rows
