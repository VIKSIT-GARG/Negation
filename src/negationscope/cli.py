import argparse
import json
import shlex
import sys
from pathlib import Path
from . import __version__
from .dataset import construct, validate
from .io import read_jsonl, write_jsonl, write_json, file_hash
from .metrics import evaluate, embedding_consistency, cosine


def parser():
    root = argparse.ArgumentParser(description="NegationScope dataset and evaluation toolkit")
    root.add_argument("--version", action="version", version=__version__)
    sub = root.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build", help="construct paired prompts from authored seeds")
    p.add_argument("--seeds", required=True); p.add_argument("--out", required=True); p.add_argument("--seed", type=int, default=42)
    p = sub.add_parser("validate")
    p.add_argument("--dataset", required=True)
    p = sub.add_parser("attach")
    p.add_argument("--dataset", required=True); p.add_argument("--manifest", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("frames")
    p.add_argument("--dataset", required=True); p.add_argument("--directory", required=True); p.add_argument("--out", required=True); p.add_argument("--count", type=int, default=8)
    p = sub.add_parser("judge")
    p.add_argument("--dataset", required=True); p.add_argument("--frames", required=True); p.add_argument("--out", required=True)
    p.add_argument("--backend", choices=["ollama", "vlmevalkit"], default="ollama")
    p.add_argument("--judge", required=True); p.add_argument("--system", required=True)
    p.add_argument("--endpoint", default="http://localhost:11434"); p.add_argument("--timeout", type=int, default=120)
    p = sub.add_parser("evaluate")
    p.add_argument("--dataset", required=True); p.add_argument("--predictions", required=True); p.add_argument("--out", required=True); p.add_argument("--seed", type=int, default=42)
    p = sub.add_parser("report")
    p.add_argument("--input", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("export-vlmevalkit")
    p.add_argument("--dataset", required=True); p.add_argument("--images", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("vbench")
    p.add_argument("--videos", required=True); p.add_argument("--out", required=True)
    p.add_argument("--dimension", choices=["subject_consistency", "background_consistency"], required=True)
    p.add_argument("--run", action="store_true", help="execute rather than print command")
    p = sub.add_parser("embeddings", help="evaluate precomputed frame and caption embeddings")
    p.add_argument("--input", required=True); p.add_argument("--out", required=True)
    return root


def main():
    args = parser().parse_args()
    try:
        c = args.command
        if c == "build":
            rows = construct(read_jsonl(args.seeds), args.seed)
            write_jsonl(args.out, rows)
            write_json(args.out + ".manifest.json", {"version": __version__, "seed": args.seed, "seed_sha256": file_hash(args.seeds), "dataset_sha256": file_hash(args.out), "summary": validate(rows)})
            print(json.dumps(validate(rows), indent=2))
        elif c == "validate":
            print(json.dumps(validate(read_jsonl(args.dataset)), indent=2))
        elif c == "attach":
            from .media import attach_media
            write_jsonl(args.out, attach_media(read_jsonl(args.dataset), read_jsonl(args.manifest)))
        elif c == "frames":
            from .media import extract_frames
            write_jsonl(args.out, extract_frames(read_jsonl(args.dataset), args.directory, args.count))
        elif c == "judge":
            from .backends import OllamaJudge, VLMEvalKitJudge, run_judge
            backend = OllamaJudge(args.judge, args.endpoint, args.timeout) if args.backend == "ollama" else VLMEvalKitJudge(args.judge)
            write_jsonl(args.out, run_judge(read_jsonl(args.dataset), read_jsonl(args.frames), backend, args.system))
        elif c == "evaluate":
            predictions = read_jsonl(args.predictions)
            report = evaluate(read_jsonl(args.dataset), predictions, args.seed)
            report["synthetic_fixture"] = any(p.get("synthetic_fixture") for p in predictions)
            report["provenance"] = {"version": __version__, "dataset_sha256": file_hash(args.dataset), "predictions_sha256": file_hash(args.predictions)}
            write_json(args.out, report)
        elif c == "report":
            from .report import render_report
            render_report(json.loads(Path(args.input).read_text()), args.out)
        elif c == "export-vlmevalkit":
            from .integrations import export_vlmevalkit
            print(json.dumps(export_vlmevalkit(read_jsonl(args.dataset), read_jsonl(args.images), args.out)))
        elif c == "vbench":
            from .integrations import vbench_plan, run_vbench
            if args.run:
                run_vbench(args.videos, args.out, args.dimension)
            else:
                print(shlex.join(vbench_plan(args.videos, args.out, args.dimension)))
        elif c == "embeddings":
            result = []
            for row in read_jsonl(args.input):
                item = {"sample_id": row["sample_id"]}
                for region in ("subject", "background"):
                    if region in row:
                        item[region] = embedding_consistency(row[region])
                if "caption_embedding" in row and "prompt_embedding" in row:
                    item["caption_prompt_cosine"] = cosine(row["caption_embedding"], row["prompt_embedding"])
                result.append(item)
            write_jsonl(args.out, result)
    except (ValueError, OSError, ImportError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
