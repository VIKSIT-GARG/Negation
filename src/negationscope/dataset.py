"""Construct matched object-presence/absence prompts from explicit scene seeds."""
import hashlib
from collections import Counter, defaultdict

KINDS = ("lexical", "morphological", "syntactic")
POSITIONS = ("begin", "middle", "end")
REQUIRED = {"scene_id", "category", "subject", "action", "setting", "target"}


def split_for(scene_id, seed):
    bucket = int(hashlib.sha256(f"{seed}:{scene_id}".encode()).hexdigest()[:8], 16) % 100
    return "train" if bucket < 70 else "validation" if bucket < 85 else "test"


def render(scene, kind, position, polarity):
    subject, action, setting, target = (scene[k] for k in ("subject", "action", "setting", "target"))
    absent = polarity == "negative"
    clauses = {
        "lexical": f"{'without' if absent else 'with'} {target}",
        "morphological": f"in a {scene['target_stem']}-free scene" if absent else f"in a scene containing {target}",
        "syntactic": f"where there is {'no ' + scene['target_stem'] if absent else target}",
    }
    clause = clauses[kind]
    if position == "begin":
        return f"{clause[0].upper() + clause[1:]}, {subject} {action} {setting}."
    if position == "middle":
        return f"{subject[0].upper() + subject[1:]}, {clause}, {action} {setting}."
    return f"{subject[0].upper() + subject[1:]} {action} {setting}, {clause}."


def construct(seeds, seed=42):
    if not seeds:
        raise ValueError("empty seed set")
    seen, rows = set(), []
    for scene in seeds:
        missing = (REQUIRED | {"target_stem"}) - scene.keys()
        if missing:
            raise ValueError(f"missing seed fields: {sorted(missing)}")
        if any(not isinstance(scene[k], str) or not scene[k].strip() for k in REQUIRED | {"target_stem"}):
            raise ValueError("seed fields must be nonempty strings")
        sid = scene["scene_id"]
        if sid in seen:
            raise ValueError(f"duplicate scene_id: {sid}")
        seen.add(sid)
        for kind in KINDS:
            for position in POSITIONS:
                pair = f"{sid}.{kind}.{position}"
                for polarity in ("positive", "negative"):
                    rows.append({
                        "sample_id": f"{pair}.{polarity}", "pair_id": pair,
                        "scene_id": sid, "category": scene["category"],
                        "negation_type": kind, "position": position, "polarity": polarity,
                        "split": split_for(sid, seed), "prompt": render(scene, kind, position, polarity),
                        "questions": [
                            {"question_id": "subject", "text": f"Is {scene['subject']} visible?", "expected": True},
                            {"question_id": "action", "text": f"Does the video show that {scene['subject']} {scene['action']}?", "expected": True},
                            {"question_id": "target", "text": f"Is {scene['target']} visible at any point in the video?", "expected": polarity == "positive"},
                        ],
                        "provenance": {"source": "negationscope-authored-seeds", "seed": seed, "schema_version": "1.0"},
                        "review_status": "needs_human_review", "media_path": None,
                    })
    validate(rows)
    return rows


def validate(rows):
    if not rows:
        raise ValueError("dataset is empty")
    ids, pairs, scenes = set(), defaultdict(list), defaultdict(set)
    for row in rows:
        for field in ("sample_id", "pair_id", "scene_id", "category", "negation_type", "position", "polarity", "split", "prompt", "questions"):
            if field not in row:
                raise ValueError(f"missing field: {field}")
        if not isinstance(row["sample_id"], str) or not row["sample_id"] or row["sample_id"] in ids:
            raise ValueError(f"invalid or duplicate sample_id: {row['sample_id']}")
        ids.add(row["sample_id"])
        if row["polarity"] not in ("positive", "negative") or row["negation_type"] not in KINDS or row["position"] not in POSITIONS:
            raise ValueError("invalid condition")
        if row["split"] not in ("train", "validation", "test"):
            raise ValueError("invalid split")
        if not isinstance(row["prompt"], str) or not row["prompt"].strip():
            raise ValueError("empty prompt")
        qs = row["questions"]
        if not isinstance(qs, list) or not qs:
            raise ValueError("questions must be a nonempty list")
        qids = [q.get("question_id") for q in qs]
        if len(set(qids)) != len(qids) or any(not isinstance(qid, str) or not qid for qid in qids):
            raise ValueError("invalid or duplicate question IDs")
        if "target" not in qids:
            raise ValueError("target question required")
        for q in qs:
            if type(q.get("expected")) is not bool or not isinstance(q.get("text"), str) or not q["text"].strip():
                raise ValueError("questions require text and boolean expected")
            if q["question_id"] == "target" and q["expected"] != (row["polarity"] == "positive"):
                raise ValueError("target truth inconsistent with polarity")
        pairs[row["pair_id"]].append(row)
        scenes[row["scene_id"]].add(row["split"])
    if any(len(splits) != 1 for splits in scenes.values()):
        raise ValueError("scene leakage across splits")
    for pair_id, members in pairs.items():
        if len(members) != 2 or {r["polarity"] for r in members} != {"positive", "negative"}:
            raise ValueError(f"incomplete pair: {pair_id}")
        for key in ("scene_id", "category", "negation_type", "position", "split"):
            if members[0][key] != members[1][key]:
                raise ValueError(f"pair metadata mismatch: {pair_id}/{key}")
        aq, bq = ({q["question_id"]: q for q in r["questions"]} for r in members)
        if aq.keys() != bq.keys() or any(aq[k]["text"] != bq[k]["text"] or (k != "target" and aq[k]["expected"] != bq[k]["expected"]) for k in aq):
            raise ValueError(f"pair questions mismatch: {pair_id}")
    return {"samples": len(rows), "pairs": len(pairs), "scenes": len(scenes),
            "categories": dict(Counter(r["category"] for r in rows)),
            "splits": dict(Counter(r["split"] for r in rows)),
            "unique_prompts": len({r["prompt"] for r in rows}),
            "review_status": dict(Counter(r.get("review_status", "unspecified") for r in rows))}
