# Evaluation methods

## Two evaluation settings

**Generator evaluation:** generate media from each prompt, then use a fixed visual judge to assess that media. Report the generator/configuration as `model` and the evaluator as `judge` in predictions. Judge error is a confound; manually audit a subset.

**VLM evaluation:** use independently human-labeled media and measure the VLM's answers against those labels. Desired prompt outcomes alone are not ground truth about an existing video. The starter dataset's expected values describe desired generation outcomes, so this second setting requires visual annotation before it can support claims about VLM accuracy.

## Strict QA and abstentions

For each sample, average binary correctness over every expected question. Missing, unknown and unparseable answers count as incorrect. Dataset-level strict QA is the mean of per-sample accuracies (macro over samples). Coverage is known answers divided by expected answers (micro over questions). If question counts vary, these denominators differ deliberately.

An all-constraints pass requires every question to be correct. Negation compliance is strict target correctness on negative samples. Forbidden presence is the fraction of negative samples answered `yes` for the target; unknowns are reported separately and must not be interpreted as verified absence.

Answers accept booleans or exact `yes`, `no`, `unknown`, `uncertain` strings, ignoring case and a trailing full stop. Free-form prose is unknown. Invalid IDs, duplicate sample/question/model predictions, incomplete pairs and inconsistent labels are errors.

## Matched-pair analysis

For each pair, gap = negative sample QA − positive sample QA. A negative gap indicates lower measured performance on the negative prompt. This is a descriptive paired difference, not causal proof of a particular internal mechanism.

Paired success requires all constraints to pass in both variants. Confidence intervals use 2,000 percentile bootstrap resamples of scene families with replacement; all variants within a selected scene stay together. They describe scene-level variation only, not generation randomness or judge uncertainty. With fewer than two independent scenes, interval bounds are null. No hypothesis-test p-values or statistical significance claims are emitted.

## Video quality: VBench

The optional bridge runs upstream `subject_consistency` and `background_consistency` in custom-input mode. See the unmodified files in `third_party/VBench/vbench/` for their actual feature extraction, normalization, frame sampling and aggregation code. Subject and background consistency are not negation metrics. Preserve upstream result files and configuration, and do not compare custom-prompt scores to standard leaderboard totals.

## Precomputed embedding diagnostics

`negationscope embeddings` accepts subject/background frame embeddings and optional caption/prompt embeddings. It computes adjacent-frame cosine and first-to-later-frame cosine, plus a caption/prompt cosine when supplied. It does not extract embeddings, segment subjects or compute official VBench scores. Store encoder, revision, preprocessing and crop/mask provenance alongside your embedding inputs.

Cosine similarity is a weak diagnostic for negation: a video containing a ball may be close in embedding space to “a dog without a ball.” No cosine threshold is used as a substitute for explicit target checking. Descriptions can omit forbidden objects and introduce hallucinations.

## Frame evidence and limits

Frames are uniformly selected with endpoints included when count > 1, capped to unique decoded indices. First-frame-only sampling is used when count = 1. Frame hashes and timestamps allow audit. A judge seeing eight frames cannot prove the target was absent throughout a video. Increase temporal sampling, use event-aware detectors, and inspect failures manually. Multi-image VLM calls treat frames as ordered images; they are not guaranteed to match a model's native video inference behavior.

## Reporting discipline

Always include system identity, judge identity, dataset hash, sample count, coverage, category/condition breakdowns and uncertainty. Do not mix predictions from different judges under one system ID. Keep technical quality, semantic compliance and human review results separate. No measured research results are provided in this release.
