from pathlib import Path
import pytest
from negationscope.dataset import construct
from negationscope.io import read_jsonl
from negationscope.metrics import evaluate, parse_answer, cosine, embedding_consistency, bootstrap_clusters


@pytest.fixture
def rows():
    return construct(read_jsonl(Path(__file__).resolve().parents[1] / "data/scene_seeds.jsonl")[:2])


def predictions(rows, answer):
    return [{"model": "test", "sample_id": r["sample_id"], "question_id": q["question_id"], "answer": answer(q)} for r in rows for q in r["questions"]]


def test_perfect(rows):
    model = evaluate(rows, predictions(rows, lambda q: q["expected"]))["models"]["test"]
    assert model["coverage"] == model["qa_accuracy_strict"] == model["negation_compliance_strict"] == model["paired_success_rate"] == 1
    assert model["negative_minus_positive_qa"] == model["forbidden_presence_rate"] == 0


def test_always_yes_cannot_pass_negation(rows):
    model = evaluate(rows, predictions(rows, lambda q: True))["models"]["test"]
    assert model["qa_accuracy_strict"] == pytest.approx(5/6)
    assert model["negation_compliance_strict"] == model["paired_success_rate"] == 0
    assert model["negative_minus_positive_qa"] == pytest.approx(-1/3)
    assert model["forbidden_presence_rate"] == 1


def test_missing_and_unknown_not_silently_dropped(rows):
    preds = predictions(rows, lambda q: None)
    model = evaluate(rows, preds[:1])["models"]["test"]
    assert model["samples"] == len(rows)
    assert model["provided_answers"] == 1
    assert model["coverage"] == model["qa_accuracy_strict"] == 0
    assert model["negative_target_unknown_rate"] == 1


def test_reject_invalid_prediction_keys(rows):
    preds = predictions(rows, lambda q: True)
    with pytest.raises(ValueError): evaluate(rows, preds + preds[:1])
    with pytest.raises(ValueError): evaluate(rows, [dict(preds[0], sample_id="bad")])
    with pytest.raises(ValueError): evaluate(rows, [])
    preds[0]["judge"] = "different"
    with pytest.raises(ValueError, match="mixed judges"): evaluate(rows, preds)


@pytest.mark.parametrize("raw,expected", [("YES.", True), ("no", False), ("unknown", None), ("not yes", None), (1, None), ("yes, probably", None)])
def test_parser_is_conservative(raw, expected):
    assert parse_answer(raw) is expected


def test_cluster_ci_and_embeddings():
    values = {"a": [0., 1.], "b": [-1., 0.]}
    assert bootstrap_clusters(values) == bootstrap_clusters(values)
    assert bootstrap_clusters({"a": [1]})["low"] is None
    assert cosine([2, 0], [1, 0]) == 1
    assert embedding_consistency([[1, 0], [0, 1]])["adjacent_cosine"] == 0
    for a, b in [([0], [1]), ([1], [1, 2]), ([float("nan")], [1])]:
        with pytest.raises(ValueError): cosine(a, b)
