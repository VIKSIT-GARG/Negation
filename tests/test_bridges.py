import base64
import csv
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from negationscope.backends import run_judge, OllamaJudge
from negationscope.dataset import construct
from negationscope.integrations import export_vlmevalkit, vbench_plan
from negationscope.io import read_jsonl, file_hash
from negationscope.media import uniform_indices, attach_media
from negationscope.report import render_report
from negationscope.metrics import evaluate


@pytest.fixture
def rows():
    return construct(read_jsonl(Path(__file__).resolve().parents[1] / "data/scene_seeds.jsonl")[:1])


def test_frame_sampling():
    assert uniform_indices(10, 3) == [0, 4, 9]
    assert uniform_indices(2, 8) == [0, 1]
    assert uniform_indices(10, 1) == [0]
    with pytest.raises(ValueError): uniform_indices(0, 8)


def test_backend_is_blind_to_answers(rows, tmp_path):
    frame = tmp_path / "frame.jpg"
    frame.write_bytes(b"fixture")
    class Judge:
        model = "stub"
        def answer(self, question, frames):
            assert isinstance(question, str) and "expected" not in question
            assert frames == [str(frame)]
            return "yes"
    manifest = [{"sample_id": row["sample_id"], "frames": [{"path": str(frame), "sha256": file_hash(frame)}]} for row in rows]
    preds = run_judge(rows, manifest, Judge(), "generator-a")
    assert len(preds) == len(rows) * 3
    assert all(p["model"] == "generator-a" and p["judge"] == "stub" for p in preds)
    frame.write_bytes(b"changed")
    with pytest.raises(ValueError): run_judge(rows, manifest, Judge(), "generator-a")


def test_ollama_payload(tmp_path):
    frame = tmp_path / "f.jpg"; frame.write_bytes(b"image")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'{"message":{"content":"no"}}'
    with patch("urllib.request.urlopen", return_value=Response()) as mocked:
        assert OllamaJudge("judge").answer("Is a ball visible?", [frame]) == "no"
        payload = json.loads(mocked.call_args.args[0].data)
        assert payload["messages"][1]["images"] == [base64.b64encode(b"image").decode()]
        assert "expected" not in json.dumps(payload)


def test_vlmevalkit_export_and_vbench_plan(rows, tmp_path):
    frame = tmp_path / "frame.jpg"; frame.write_bytes(b"fixture-image")
    manifest = [{"sample_id": r["sample_id"], "image_path": str(frame)} for r in rows]
    output = tmp_path / "questions.tsv"
    assert export_vlmevalkit(rows, manifest, output)["rows"] == 54
    with output.open() as stream: exported = list(csv.DictReader(stream, delimiter="\t"))
    assert {r["answer"] for r in exported} == {"A", "B"}
    assert base64.b64decode(exported[0]["image"]) == b"fixture-image"
    plan = vbench_plan(tmp_path, tmp_path / "results", "subject_consistency")
    assert "--mode=custom_input" in plan
    with pytest.raises(ValueError): vbench_plan(tmp_path, tmp_path, "invented")


def test_attach_validates_media(rows, tmp_path):
    video = tmp_path / "f.mp4"; video.write_bytes(b"fixture")
    manifest = [{"sample_id": rows[0]["sample_id"], "media_path": str(video), "generator": "test", "seed": 1}]
    attached = attach_media(rows, manifest)
    assert attached[0]["media_sha256"] == file_hash(video)
    assert attached[0]["generation"]["seed"] == 1
    with pytest.raises(ValueError): attach_media(rows, manifest * 2)


def test_report_escapes_model_names(rows, tmp_path):
    predictions = [{"model": "<script>alert(1)</script>", "sample_id": r["sample_id"], "question_id": q["question_id"], "answer": True} for r in rows for q in r["questions"]]
    report = evaluate(rows, predictions)
    output = tmp_path / "report.html"; render_report(report, output)
    assert "<script>" not in output.read_text()
    assert "&lt;script&gt;" in output.read_text()
