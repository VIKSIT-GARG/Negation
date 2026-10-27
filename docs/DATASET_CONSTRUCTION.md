# Dataset construction

## Implemented pipeline

1. Author a scene with a subject, action, setting and a single target object. Store the target with an article (`a ball`) and an article-free stem (`ball`).
2. Render nine conditions: three surface forms × three clause positions.
3. For each condition, create a matched presence/absence pair. Only the target's truth changes.
4. Add positive subject/action questions and a shared target-presence question. Avoid putting negative wording in the target question itself.
5. Assign train/validation/test with a deterministic SHA-256 bucket of `seed:scene_id` (70/15/15 thresholds). All paraphrases, conditions and polarities from that scene stay together. Small sets need not have exact split percentages.
6. Validate pairs, labels and questions. Export a JSONL dataset, a build manifest and content hashes.
7. Review the prompts, attach generated videos, and verify visual outcomes separately. A generated prompt is not evidence that a video satisfies it.

## Operational language categories

| Label | Negative template | Positive control |
|---|---|---|
| lexical | without a ball | with a ball |
| morphological | in a ball-free scene | in a scene containing a ball |
| syntactic | where there is no ball | where there is a ball |

These are project-specific operational labels, not mutually exclusive linguistic categories. `without` has grammatical properties; `no` can be categorized differently under other taxonomies. The morphological condition specifically uses the privative `-free` construction; it does not test every negative affix. Positive controls are matched in semantics but not always length or tokenization. Treat the result as a controlled template study.

## Position manipulation

The same target clause appears before the main clause, as a parenthetical after the subject, or after the main clause. This controls clause position, not exact token offset. Punctuation, token count and fluency can affect scores. Collect human fluency judgments before using the suite for research conclusions.

## Human review fields

Change `review_status` from `needs_human_review` only after checking:

- The target is not required by the subject/action (avoid, for example, a cyclist without any bicycle).
- The negative target is visually distinguishable from related categories.
- Both prompts are feasible and preserve the same primary activity and setting.
- The positive target has sufficient visibility in a successful generated video.
- The category and clause form are correctly annotated.

The provided 36 scenes are authored starting points, not expert-validated benchmark data. The current categories are broad scene domains; all manipulated targets are object-presence conditions. The package does not yet generate action negation, temporal negation, causal exclusions or arbitrary nested logical scope.

## Connection to NegBench

NegBench's retained scripts begin from captions and visual media, extract present objects, propose and filter absent objects, then construct and paraphrase MCQ/retrieval examples. Our paired T2V builder begins from explicit scene seeds and desired output constraints instead. It must not infer actual absence in real media from a caption's silence. Use the upstream filtering pipeline and human review if extending to existing images/video.

Relevant retained files are listed in `docs/SOURCE_MAP.md`; the original upstream evaluation construction README is preserved beside those scripts. Download underlying datasets only under their own terms.
