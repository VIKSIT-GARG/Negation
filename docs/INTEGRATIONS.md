# Integration guide

## VBench

Install the full upstream project in a dedicated environment following its own README. Its dependencies and checkpoints are intentionally not installed by the core package. The pinned revision is recorded in `upstream.lock.json`.

```bash
negationscope vbench --videos media/generator-a --out runs/vbench-a --dimension subject_consistency
# Inspect the printed argument list, then run it:
negationscope vbench --videos media/generator-a --out runs/vbench-a --dimension subject_consistency --run
negationscope vbench --videos media/generator-a --out runs/vbench-a --dimension background_consistency --run
```

The bridge invokes the official `vbench evaluate` CLI with `--mode=custom_input` and `--output_path`. It preserves upstream output rather than renaming a local approximation as VBench. The `vbench` executable must be available in the active PATH. The package's bridge has contract tests; a full upstream checkpoint run was not performed in this environment.

## VLMEvalKit live judge

Install the full upstream repository in an environment appropriate for your chosen model. Install NegationScope into that environment too. The adapter instantiates `vlmeval.config.supported_VLM[model]()` and calls the public `generate(message=...)` interface with ordered image entries followed by a question.

```bash
negationscope judge --backend vlmevalkit --judge REGISTERED_MODEL_NAME \
  --system GENERATOR_AND_CONFIG --dataset runs/attached.jsonl \
  --frames runs/frames.jsonl --out runs/predictions.jsonl
```

Model keys and required credentials depend on the installed VLMEvalKit revision. Configure credentials using its documented environment variables, outside this repository. Models must accept multiple images; lower-VRAM devices may need fewer/smaller frames or an external inference server. The adapter does not promise every registered model is compatible. A live VLMEvalKit inference was not run here.

## VLMEvalKit single-image TSV export

Provide `sample_id,image_path` records as JSONL (example: `examples/image_manifest.jsonl`). Then:

```bash
negationscope export-vlmevalkit --dataset runs/prompts.jsonl \
  --images runs/images.jsonl --out runs/NegationScopeMCQ.tsv
```

The table has `index,image,question,A,B,answer,category` plus tracing fields. Images are embedded as base64. A=Yes, B=No, and expected labels are mapped to answer letters. Use the full upstream custom dataset workflow to register/run the TSV. This is a format export, not automatic dataset registration, and single-image evaluation cannot establish temporal absence or actions across a whole video.

## Ollama

Start your local Ollama server, install a vision-capable model separately and use the exact local model name with `--judge`. The adapter posts to `/api/chat` with temperature zero, ordered base64 frames, and a visual-only question. It retries transient 429/5xx/network failures at most twice. Other errors abort; no successful report is manufactured after an inference failure. A live inference was not run here; the HTTP payload is covered by a mock contract test.

## NegBench original construction/evaluation

The snapshot contains the original absent-object mining, verification, MCQ/paraphrase and video construction scripts, plus MCQ and retrieval evaluators. They depend on the full original project and additional libraries such as PyTorch, pandas, vLLM and transformers. Use the original README preserved at `third_party/NegBench/synthetic_datasets/evaluation/README.md` and the upstream root README for complete installation.

Do not import those study snapshots as `negationscope` modules. To run the original benchmark, check out its pinned revision separately. The local JSONL schema is a new paired generation-task schema, not a drop-in replacement for every original NegBench CSV format.
