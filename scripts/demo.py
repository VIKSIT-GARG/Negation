"""Generate explicitly synthetic scoring fixtures; never model measurements."""
import argparse
from pathlib import Path
from negationscope.dataset import construct
from negationscope.io import read_jsonl, write_json, write_jsonl
from negationscope.metrics import evaluate
from negationscope.report import render_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="runs/demo")
    args = parser.parse_args()
    output = Path(args.out)
    root = Path(__file__).resolve().parents[1]
    dataset = construct(read_jsonl(root / "data/scene_seeds.jsonl"))
    predictions = []
    for model in ("fixture-perfect", "fixture-always-yes", "fixture-abstaining"):
        for row in dataset:
            for q in row["questions"]:
                answer = q["expected"] if model == "fixture-perfect" else True if model == "fixture-always-yes" else None
                predictions.append({"model": model, "sample_id": row["sample_id"], "question_id": q["question_id"],
                                    "answer": answer, "synthetic_fixture": True})
    write_jsonl(output / "dataset.jsonl", dataset)
    write_jsonl(output / "predictions.jsonl", predictions)
    report = evaluate(dataset, predictions)
    report["synthetic_fixture"] = True
    write_json(output / "report.json", report)
    render_report(report, output / "report.html")
    print(f"Synthetic demonstration saved: {output / 'report.html'}")


if __name__ == "__main__":
    main()
