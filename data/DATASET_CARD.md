# NegationScope starter prompt suite

- **Creator:** Viksit Garg; scene seeds assembled for this personal framework.
- **Version:** 0.1.0.
- **Scope:** English prompt-controlled object presence/absence in generated video.
- **Source:** 36 newly authored structured scenes; no third-party images, videos, captions or private datasets.
- **Composition:** 18 scene-domain categories × 2 scenes × 3 surface forms × 3 positions × 2 polarities = 648 rows.
- **Statistical unit:** 36 scene families, not 648 independent examples.
- **Ground truth:** Desired generation constraints. Requires separate visual annotation for evaluating a VLM on existing media.
- **Splits:** Stable scene-level SHA-256 split with 70/15/15 thresholds; small-set proportions vary.
- **Review:** All generated prompts begin as `needs_human_review`; no expert validation is claimed.
- **License:** MIT for these authored text seeds and original construction code. External media/checkpoints carry their own terms.
- **Known limitations:** Template repetition, modest scene diversity, English only, one target object, no action/temporal/causal negation, potentially unnatural compound adjectives, sparse-frame evidence limits.
- **Intended uses:** Software testing, pipeline prototyping, controlled pilot studies after review.
- **Unsuitable claims:** Validated general benchmark, replicated internship dataset, measured model ranking, comprehensive assessment of linguistic negation.
