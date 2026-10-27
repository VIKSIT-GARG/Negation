"""Optional VLM backends. Ground-truth labels are never sent to the judge."""
import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from .io import file_hash
from .metrics import parse_answer

INSTRUCTION = "Frames are in chronological order. Answer the visual question using only the frames. Reply with exactly yes, no, or unknown. Use unknown when the visual evidence is insufficient."


class OllamaJudge:
    def __init__(self, model, endpoint="http://localhost:11434", timeout=120):
        self.model, self.endpoint, self.timeout = model, endpoint.rstrip("/"), timeout

    def answer(self, question, frames):
        payload = {"model": self.model, "stream": False, "options": {"temperature": 0},
                   "messages": [{"role": "system", "content": INSTRUCTION},
                                {"role": "user", "content": question,
                                 "images": [base64.b64encode(Path(p).read_bytes()).decode() for p in frames]}]}
        request = urllib.request.Request(self.endpoint + "/api/chat", json.dumps(payload).encode(), {"Content-Type": "application/json"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return json.load(response)["message"]["content"]
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise
            except (urllib.error.URLError, TimeoutError):
                if attempt == 2:
                    raise
            time.sleep(2 ** attempt)


class VLMEvalKitJudge:
    def __init__(self, model):
        from vlmeval.config import supported_VLM
        if model not in supported_VLM:
            raise ValueError(f"model not registered in VLMEvalKit: {model}")
        self.model = model
        self.client = supported_VLM[model]()

    def answer(self, question, frames):
        message = [{"type": "image", "value": str(Path(p).resolve())} for p in frames]
        message.append({"type": "text", "value": INSTRUCTION + "\n" + question})
        return self.client.generate(message=message)


def run_judge(dataset, frame_manifest, backend, system):
    """Return all predictions; abort on transport errors instead of reporting a fake result."""
    from .dataset import validate
    validate(dataset)
    mapping = {}
    for entry in frame_manifest:
        sid = entry["sample_id"]
        if sid in mapping:
            raise ValueError(f"duplicate frame manifest entry: {sid}")
        mapping[sid] = entry
    if set(mapping) != {r["sample_id"] for r in dataset}:
        raise ValueError("frame manifest must match dataset sample IDs exactly")
    predictions = []
    for row in dataset:
        frames = mapping[row["sample_id"]]["frames"]
        if not frames:
            raise ValueError("empty frame list")
        if row.get("media_sha256") and mapping[row["sample_id"]].get("media_sha256") != row["media_sha256"]:
            raise ValueError("frame manifest source does not match attached media")
        for frame in frames:
            if file_hash(frame["path"]) != frame["sha256"]:
                raise ValueError(f"frame changed: {frame['path']}")
        for q in row["questions"]:
            raw = backend.answer(q["text"], [frame["path"] for frame in frames])
            predictions.append({"sample_id": row["sample_id"], "question_id": q["question_id"],
                                "model": system, "judge": backend.model, "raw_answer": raw,
                                "answer": parse_answer(raw),
                                "frame_sha256": [f["sha256"] for f in frames]})
    return predictions
