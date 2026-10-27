"""Explicit export and invocation bridges; upstream metrics keep their identity."""
import base64
import csv
import shutil
import subprocess
from pathlib import Path
from .dataset import validate


def export_vlmevalkit(dataset, image_manifest, output):
    """Single-image yes/no MCQ TSV. This export does not evaluate temporal claims."""
    validate(dataset)
    mapping = {}
    for entry in image_manifest:
        if entry["sample_id"] in mapping:
            raise ValueError("duplicate image manifest ID")
        mapping[entry["sample_id"]] = entry["image_path"]
    if set(mapping) != {r["sample_id"] for r in dataset}:
        raise ValueError("image manifest must match dataset exactly")
    fields = ["index", "sample_id", "question_id", "image", "question", "A", "B", "answer", "category", "split"]
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, delimiter="\t")
        writer.writeheader()
        index = 0
        for row in dataset:
            image = base64.b64encode(Path(mapping[row["sample_id"]]).read_bytes()).decode()
            for q in row["questions"]:
                writer.writerow({"index": index, "sample_id": row["sample_id"], "question_id": q["question_id"],
                                 "image": image, "question": q["text"], "A": "Yes", "B": "No",
                                 "answer": "A" if q["expected"] else "B", "category": row["category"], "split": row["split"]})
                index += 1
    return {"rows": index, "task": "single-frame MCQ", "output": str(output)}


def vbench_plan(videos, output, dimension):
    if dimension not in ("subject_consistency", "background_consistency"):
        raise ValueError("bridge supports subject_consistency or background_consistency")
    source = Path(videos).resolve()
    if not source.exists():
        raise ValueError(f"missing videos: {source}")
    return ["vbench", "evaluate", "--videos_path", str(source), "--dimension", dimension,
            "--mode=custom_input", "--output_path", str(Path(output).resolve())]


def run_vbench(videos, output, dimension):
    command = vbench_plan(videos, output, dimension)
    if not shutil.which("vbench"):
        raise RuntimeError("Install upstream VBench in its own environment first; see docs/INTEGRATIONS.md")
    subprocess.run(command, check=True)  # argument list; no shell interpolation
