"""Strict QA scoring and scene-clustered paired uncertainty estimates."""
import math
import random
from collections import defaultdict
from statistics import mean
from .dataset import validate


def parse_answer(answer):
    if answer is None or type(answer) is bool:
        return answer
    if isinstance(answer, str):
        return {"yes": True, "no": False, "unknown": None, "uncertain": None}.get(answer.strip().lower().rstrip("."))
    return None


def bootstrap_clusters(values_by_scene, seed=42, repeats=2000):
    """Resample scenes, retain all prompt variants within each sampled scene."""
    clusters = list(values_by_scene.values())
    if not clusters:
        return None
    if len(clusters) < 2:
        return {"low": None, "high": None, "reason": "fewer than two independent scenes"}
    rng = random.Random(seed)
    estimates = sorted(mean(v for cluster in rng.choices(clusters, k=len(clusters)) for v in cluster) for _ in range(repeats))
    return {"low": estimates[int(.025 * repeats)], "high": estimates[min(repeats - 1, int(.975 * repeats))], "method": "scene-cluster percentile bootstrap", "repeats": repeats}


def evaluate(dataset, predictions, seed=42):
    validate(dataset)
    lookup = {r["sample_id"]: r for r in dataset}
    indexed, models, judges = {}, set(), defaultdict(set)
    for p in predictions:
        if not isinstance(p.get("model"), str) or not p["model"].strip():
            raise ValueError("prediction requires model")
        sid, qid = p.get("sample_id"), p.get("question_id")
        if sid not in lookup or qid not in {q["question_id"] for q in lookup[sid]["questions"]}:
            raise ValueError(f"unknown sample/question: {sid}/{qid}")
        key = (p["model"], sid, qid)
        if key in indexed:
            raise ValueError(f"duplicate prediction: {key}")
        indexed[key] = parse_answer(p.get("answer"))
        models.add(p["model"])
        judges[p["model"]].add(p.get("judge", "unspecified"))
    if not models:
        raise ValueError("no predictions")
    if any(len(names) != 1 for names in judges.values()):
        raise ValueError("mixed judges under one system ID; use separate runs/system IDs")
    report = {"schema_version": "1.0", "seed": seed, "models": {}}
    for model in sorted(models):
        scored, groups, total, known, provided = [], defaultdict(list), 0, 0, 0
        for row in dataset:
            hits, target_hit, target_answer, observed = [], 0, None, 0
            for q in row["questions"]:
                key = (model, row["sample_id"], q["question_id"])
                answer = indexed.get(key)
                provided += key in indexed
                known += answer is not None
                total += 1
                observed += answer is not None
                hit = int(answer is not None and answer == q["expected"])
                hits.append(hit)
                if q["question_id"] == "target":
                    target_hit, target_answer = hit, answer
            item = {"sample_id": row["sample_id"], "pair_id": row["pair_id"], "scene_id": row["scene_id"],
                    "polarity": row["polarity"], "qa_accuracy": mean(hits), "all_constraints_pass": int(all(hits)),
                    "target_correct": target_hit, "target_answer": target_answer,
                    "known_answers": observed, "expected_answers": len(hits)}
            scored.append(item)
            for field in ("category", "negation_type", "position", "polarity", "split"):
                groups[f"{field}:{row[field]}"].append(item)
        pairs = defaultdict(dict)
        for item in scored:
            pairs[item["pair_id"]][item["polarity"]] = item
        gaps, pair_success = defaultdict(list), []
        for pair in pairs.values():
            pos, neg = pair["positive"], pair["negative"]
            gaps[pos["scene_id"]].append(neg["qa_accuracy"] - pos["qa_accuracy"])
            pair_success.append(int(pos["all_constraints_pass"] and neg["all_constraints_pass"]))
        negatives = [r for r in scored if r["polarity"] == "negative"]
        report["models"][model] = {
            "judge": next(iter(judges[model])),
            "samples": len(scored), "expected_answers": total, "provided_answers": provided,
            "coverage": known / total, "qa_accuracy_strict": mean(r["qa_accuracy"] for r in scored),
            "all_constraints_pass_rate": mean(r["all_constraints_pass"] for r in scored),
            "negation_compliance_strict": mean(r["target_correct"] for r in negatives),
            "forbidden_presence_rate": mean(int(r["target_answer"] is True) for r in negatives),
            "negative_target_unknown_rate": mean(int(r["target_answer"] is None) for r in negatives),
            "paired_success_rate": mean(pair_success),
            "negative_minus_positive_qa": mean(v for cluster in gaps.values() for v in cluster),
            "gap_95_ci": bootstrap_clusters(gaps, seed),
            "groups": {key: {"n": len(items), "qa_accuracy_strict": mean(i["qa_accuracy"] for i in items),
                              "all_constraints_pass_rate": mean(i["all_constraints_pass"] for i in items)} for key, items in sorted(groups.items())},
            "per_sample": scored,
        }
    return report


def cosine(a, b):
    if not a or len(a) != len(b) or any(not math.isfinite(x) for x in [*a, *b]):
        raise ValueError("embeddings must be finite, nonempty, and equally sized")
    norm = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    if norm == 0:
        raise ValueError("zero embedding norm")
    return max(-1., min(1., sum(x*y for x, y in zip(a, b)) / norm))


def embedding_consistency(embeddings):
    """Adjacent and first-frame cosine averages; a diagnostic, not VBench."""
    if len(embeddings) < 2:
        raise ValueError("at least two frame embeddings required")
    return {"adjacent_cosine": mean(cosine(a, b) for a, b in zip(embeddings, embeddings[1:])),
            "first_frame_cosine": mean(cosine(embeddings[0], b) for b in embeddings[1:])}
