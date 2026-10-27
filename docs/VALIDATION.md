# Validation record

Validated on 27 October 2026 using Python 3.12 in the build environment.

| Check | Outcome |
|---|---|
| `python -m pytest -q` | 26 passed |
| Upstream file hashes | 18 files verified across 3 projects |
| Dataset construction | 648 records, 324 complete pairs, 36 scenes, 18 categories |
| Split leakage | Scene families remain within one split |
| Actual video encode/decode | Five-frame synthetic MJPEG clip decoded; selected frames 0, 2 and 4 with expected timestamps |
| Changed-media handling | Hash mismatch rejected |
| Strict QA controls | Perfect, always-yes and abstaining manufactured responses behave as expected |
| Backend contract | Ollama request payload and answer blindness checked with a mock response |
| Report export | Demo and CLI JSON-to-HTML exports succeeded; model names escaped |
| Source compilation | Original package, tests and scripts compiled successfully |

No real visual model inference, text-to-video generation, upstream VBench checkpoint evaluation or live VLMEvalKit inference was performed. Their integration contracts and setup instructions are included. The optional video path was exercised with installed OpenCV; the core suite skips that test when the video dependency is absent.

The demo report contains synthetic fixtures only. It must not be presented as evidence of any model's measured performance or of internship results.
