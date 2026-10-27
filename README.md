<div align="center">

# NegationScope
### Dataset construction & evaluation for negation in visual models

**A personal research framework by [Viksit Garg](https://github.com/VIKSIT-GARG)**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Core](https://img.shields.io/badge/Core-zero%20dependencies-087f8c)
![License](https://img.shields.io/badge/Original%20code-MIT-68b684)
![Research](https://img.shields.io/badge/Focus-Negation%20%26%20Video%20Evaluation-8559da)

**Construct controlled prompts. Inspect visual evidence. Measure compliance.**

</div>

NegationScope builds matched positive/negative prompt datasets and evaluates whether visual outputs satisfy their constraints. It connects three complementary research directions: **NegBench's negation tasks**, **VLMEvalKit's model evaluation interfaces**, and **VBench's video quality dimensions**.

The project is aligned with the research topic **“Evaluation of Negation understanding in Text-to-video models.”** This is a new personal implementation and an attributed collection of selected public upstream code. It does not represent the original internship source code, an institutional release, or a reproduction of internship measurements. All included scenes are newly authored examples; no internal data or results are included.

## What is implemented

| Component | Included implementation |
|---|---|
| Dataset construction | 36 authored scene seeds across 18 categories; lexical, morphological and syntactic templates; begin/middle/end placement; matched positive/negative pairs |
| Validation | Unique IDs, pair completeness, condition checks, target ground truth, matched questions, and scene-level split isolation |
| Experiment records | JSONL manifests; media, dataset, frame and prediction hashes; generation metadata fields |
| Visual evidence | Uniform frame sampling with source indices and timestamps, using optional OpenCV |
| VLM evaluation | Local Ollama API and optional installed VLMEvalKit model registry; judge receives frames and questions only |
| Scoring | Strict QA, all-constraint success, negation compliance, forbidden presence, unknown rate, pair success and paired gaps |
| Uncertainty | Scene-cluster bootstrap for the negative-minus-positive QA gap |
| Video diagnostics | Separate upstream VBench invocation for subject/background consistency; optional precomputed embedding diagnostics |
| Reporting | JSON results and a standalone HTML report with condition breakdowns |
| Upstream study code | 18 files, including licenses, retained under original ownership in `third_party/`; exact revisions and hashes in `upstream.lock.json` |

**Status:** runnable core and synthetic fixture demo. No real model scores are bundled. Live VLM inference and upstream GPU metrics need models, media, and their separate environments.

## Start in one minute

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python scripts/check_provenance.py
python scripts/demo.py
```

Open `runs/demo/report.html`. The three systems are intentionally named `fixture-perfect`, `fixture-always-yes`, and `fixture-abstaining`: their answers are manufactured to verify scoring, **not measured model performance**.

Build the prompt dataset separately:

```bash
negationscope build --seeds data/scene_seeds.jsonl --out runs/prompts.jsonl --seed 42
negationscope validate --dataset runs/prompts.jsonl
```

This produces **648 prompt records / 324 matched pairs / 36 scene families / 18 categories**. These are template variations, not 648 independent scenes. All variants of a scene share a split. Prompts start as `needs_human_review`.

## Example: one controlled contrast

| Positive prompt | Negative prompt |
|---|---|
| With a ball, a dog runs in a park. | Without a ball, a dog runs in a park. |

Both records ask the judge the same questions:

1. Is a dog visible?
2. Does the video show that a dog runs?
3. Is a ball visible at any point in the video?

The target answer flips from **yes** to **no**, while subject and action constraints remain positive. The judge never sees the expected answer, polarity or generation prompt. This reduces direct answer leakage; it does not eliminate model judgment errors.

## Evaluate actual videos

Generate videos with your chosen generator outside this package. Record the output corresponding to each `sample_id` in a media manifest; see [the schema](docs/SCHEMA.md). All CLI paths are relative to the current working directory unless absolute.

```bash
python -m pip install -e '.[video]'
negationscope attach --dataset runs/prompts.jsonl --manifest runs/media.jsonl --out runs/attached.jsonl
negationscope frames --dataset runs/attached.jsonl --directory runs/frames --out runs/frames.jsonl --count 8

# Start Ollama separately and pull a vision-capable judge that fits your machine.
negationscope judge --dataset runs/attached.jsonl --frames runs/frames.jsonl \
  --judge YOUR_LOCAL_VISION_MODEL --system YOUR_GENERATOR_AND_CONFIG \
  --out runs/predictions.jsonl

negationscope evaluate --dataset runs/attached.jsonl --predictions runs/predictions.jsonl --out runs/results.json
negationscope report --input runs/results.json --out runs/report.html
```

For a small first run, retain a few **complete pairs** in your dataset. The frame manifest passed to `judge` must match that subset exactly. Default execution is serial and does not download or select a model for you.

`--system` identifies the generator/configuration being assessed; `--judge` identifies the visual evaluator. Use separate runs for different judge configurations. More detail: [integration guide](docs/INTEGRATIONS.md).

## How the upstream projects are used

| Project | Retained source | Role in NegationScope |
|---|---|---|
| [NegBench](https://github.com/m1k2zoo/negbench) | Caption concept extraction, absent-object filtering, MCQ construction, paraphrasing, video tasks, MCQ/retrieval evaluation | Source study of data construction and negation tasks; our paired T2V JSONL builder is separately implemented |
| [VLMEvalKit](https://github.com/open-compass/VLMEvalKit) | Base model and image dataset interfaces | Optional live model registry adapter; single-image MCQ TSV export |
| [VBench](https://github.com/Vchitect/VBench) | Subject/background consistency implementations, engine and CLI | Optional command bridge to installed upstream metrics; quality results stay separate from compliance |

The source snapshots are **selected study files**, not full standalone installations. Install upstream projects separately to run their full pipelines. Their authors retain credit for their methods and code; original NegationScope modules are under `src/negationscope/`. See [source map](docs/SOURCE_MAP.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Repository guide

```text
src/negationscope/   dataset, scoring, media, backends, integrations, reports, CLI
data/               original seed scenes and dataset card
examples/           input format examples and labeled synthetic report
docs/               methods, schema, experiments, source map, integrations
third_party/        unmodified, attributed upstream source snapshots
scripts/            demo, provenance check, GitHub publishing helper
tests/              core correctness and adapter contract tests
upstream.lock.json  exact upstream commit IDs and file hashes
```

Read [dataset construction](docs/DATASET_CONSTRUCTION.md), [evaluation methods](docs/METHODS.md), and [experiment protocol](docs/EXPERIMENTS.md) for the research design and its limits. A sampled-frame judge can miss brief events; embedding similarity can miss negation; temporal consistency alone does not establish prompt adherence.

## Attribution and citation

Original framework copyright © 2026 Viksit Garg, MIT licensed. Third-party snapshots retain their MIT or Apache-2.0 licenses. Dataset and checkpoint licenses are separate from code licenses.

If you build on this project, cite the relevant upstream papers in [references.bib](references.bib) as well as this software release using [CITATION.cff](CITATION.cff). The personal framework does not claim authorship of VBench, VLMEvalKit or NegBench.
