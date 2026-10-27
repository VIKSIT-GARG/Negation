# Reproducible experiment protocol

1. Build and hash the dataset. Review the prompts and freeze a version before running models.
2. Select complete pairs from held-out scene families. Keep model development and judge calibration away from the final test scenes.
3. Fix generator checkpoint, resolution, duration, FPS, seed policy, inference steps and guidance. Record generation failures; do not silently discard them.
4. Generate both polarities with matched settings. Store one media mapping per sample/configuration. Use separate run directories for seed replicates.
5. Freeze judge model/revision, instructions, inference settings and frame policy. Audit human agreement on a prespecified subset.
6. Extract frames and preserve source/frame hashes. Run the judge and strict evaluation; inspect unknowns and raw outputs.
7. Run video quality metrics separately. Preserve upstream environment versions and checkpoint identifiers with raw outputs.
8. Report all samples, coverage, strict adherence, target compliance, paired success, paired gaps and scene-cluster intervals. Separate hypothesis generation from confirmatory results.

## Suggested experiment directory

```text
runs/experiment-a/
  experiment.json          generator/judge revisions and exact settings
  prompts.jsonl            frozen complete pairs
  prompts.jsonl.manifest.json
  media.jsonl              generated file mapping and seeds
  attached.jsonl           media hashes
  frames.jsonl             sampled evidence records
  predictions.jsonl        raw/parsed answers
  results.json             strict metrics and source hashes
  report.html              portable summary
  vbench/                  unchanged upstream output
```

## Controls worth running

- Always-yes and always-no evaluators reveal answer-prior sensitivity. Fixture tests are software checks, not models.
- Balanced question phrasing and manually verified clips help distinguish judge bias from generator failures.
- Compare prompt forms and clause position within scene families; the current suite changes text length and fluency as well.
- Inspect short target appearances missed by sparse frame sampling.
- Repeat generation seeds. The built-in bootstrap clusters scenes only; use a hierarchical analysis if treating seeds as another random factor.

## What a result may support

A fixed judge's strict target scores on a frozen paired prompt suite can describe measured compliance under that protocol. It does not establish universal language understanding, human-equivalent visual recognition, causal attribution to negation, or equivalence to official benchmark leaderboard scores.

No results from DRDO or any internship project are asserted in this repository. Fill experiment metadata with measurements only after actually running the models.
