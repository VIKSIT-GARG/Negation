# Data formats

All files use UTF-8. JSONL means one JSON object per line. CLI paths resolve against the current working directory. Samples include a `provenance` dictionary and a `review_status` field in addition to the required condition metadata.

## Seed

```json
{"scene_id":"scene-001","category":"animals","subject":"a dog","action":"runs","setting":"in a park","target":"a ball","target_stem":"ball"}
```

## Constructed sample

```json
{"sample_id":"scene-001.lexical.begin.negative","pair_id":"scene-001.lexical.begin","scene_id":"scene-001","category":"animals","negation_type":"lexical","position":"begin","polarity":"negative","split":"train","prompt":"Without a ball, a dog runs in a park.","questions":[{"question_id":"subject","text":"Is a dog visible?","expected":true},{"question_id":"action","text":"Does the video show that a dog runs?","expected":true},{"question_id":"target","text":"Is a ball visible at any point in the video?","expected":false}]}
```

Split above is illustrative; the builder computes the actual split. The matching positive record must also be present for validation and scoring.

## Media mapping

```json
{"sample_id":"scene-001.lexical.begin.negative","media_path":"media/sample-negative.mp4","generator":"your-generator","generator_revision":"exact-checkpoint-revision","seed":42,"guidance_scale":6.0,"steps":30,"duration_seconds":5}
```

`attach` verifies file existence and adds a content hash. Partial mappings are allowed at attach time; `frames` requires media for every sample in its input. Use separate datasets/runs for different generator configurations. The runner does not automatically generate videos.

## Frame mapping

```json
{"sample_id":"scene-001.lexical.begin.negative","media_sha256":"actual-source-hash","frames":[{"path":"runs/frames/frame.jpg","frame_index":0,"time_seconds":0.0,"sha256":"actual-frame-hash"}]}
```

The extractor fills the actual hashes. The judge verifies frame bytes and attached source identity before using them. It does not receive labels, prompt text, sample metadata or generation settings.

## Prediction

```json
{"model":"generator-a-seed42","judge":"your-vlm","sample_id":"scene-001.lexical.begin.negative","question_id":"target","answer":false,"raw_answer":"no"}
```

One record per system/sample/question. Null means unknown. Omitted records remain in strict denominators as failures. Unknown sample/question IDs and duplicate records are rejected. Keep model IDs unique across judge/configuration changes. External predictions can be scored without running a built-in backend.

## Embeddings

```json
{"sample_id":"example","subject":[[1,0],[0.9,0.1]],"background":[[0,1],[0.1,0.9]],"caption_embedding":[1,0],"prompt_embedding":[0.8,0.2]}
```

All vectors must be finite, equally sized, nonzero vectors. Subject/background sequences each require at least two frames. These are diagnostics, separate from official VBench.
