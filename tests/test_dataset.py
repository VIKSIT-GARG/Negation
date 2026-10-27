import copy
from pathlib import Path
import pytest
from negationscope.dataset import construct, validate, split_for
from negationscope.io import read_jsonl

SEEDS = read_jsonl(Path(__file__).resolve().parents[1] / "data/scene_seeds.jsonl")


def test_balanced_pairs_and_stable_build():
    rows = construct(SEEDS)
    summary = validate(rows)
    assert summary["samples"] == 648
    assert summary["pairs"] == 324
    assert summary["scenes"] == 36
    assert len(summary["categories"]) == 18
    assert all(n == 36 for n in summary["categories"].values())
    assert rows == construct(list(SEEDS))
    for scene in SEEDS:
        assert len({r["split"] for r in rows if r["scene_id"] == scene["scene_id"]}) == 1
    assert {split_for(s["scene_id"], 42) for s in SEEDS} == {"train", "validation", "test"}


@pytest.mark.parametrize("problem", ["duplicate", "missing_pair", "leakage", "target_truth", "question_mismatch", "empty"])
def test_invalid_dataset(problem):
    rows = copy.deepcopy(construct(SEEDS[:1]))
    if problem == "duplicate": rows.append(rows[0])
    if problem == "missing_pair": rows.pop()
    if problem == "leakage": rows[0]["split"] = "test" if rows[0]["split"] != "test" else "train"
    if problem == "target_truth": rows[0]["questions"][-1]["expected"] = False
    if problem == "question_mismatch": rows[0]["questions"][0]["text"] = "Changed?"
    if problem == "empty": rows = []
    with pytest.raises(ValueError): validate(rows)


def test_seed_validation():
    with pytest.raises(ValueError): construct([SEEDS[0], SEEDS[0]])
    with pytest.raises(ValueError): construct([{"scene_id": "incomplete"}])
