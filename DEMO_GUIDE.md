# NegationScope: reproducible college demonstration

This add-on runs inside the original **VIKSIT-GARG/Negation** repository.

## Start

Requires Python >= 3.10 and Bash (Linux, macOS, WSL or Git Bash with Python on PATH). **NumPy must be installed (`python3 -m pip install numpy`). No GPU, cloud API or model download is needed.** On Windows without Bash use `python dashboard/server.py` with `PYTHONPATH=src`, or WSL.

1. Install NumPy using `python3 -m pip install numpy`, then copy `run.sh`, `dashboard/`, and `tests/test_college_demo.py` into the root of the Negation repository (keeping the repo's original `src/`, `data/`, and `scripts/`).
2. From the repository root run `bash run.sh` (or `chmod +x run.sh && ./run.sh`).
3. Open `http://127.0.0.1:8765` on the same computer.
4. Optional: set `PORT=8888 bash run.sh` to use another port.

**Live verification**: `bash run.sh test` executes the new standard-library tests plus the actual existing dataset builder and validator. `bash run.sh generate` regenerates the original synthetic demo HTML/JSON fixtures in `runs/college-demo/`.

## Four-minute live presentation

1. Explain the umbrella prompt pair: realistic generation can violate a negative constraint.
2. Show the **648** template records, **324** paired prompts, **36** authored scenes and **18** categories, using the real dataset builder.
3. Compare programmed **perfect / always yes / always no / abstain** answer policies. Their scoring changes are computed by the repository's real `negationscope.metrics.evaluate()` function, but they are **not VLM/video results**.
4. Pick an authored prompt pair. Under **Live Constraint Test**, click **No** (correct for object exclusion), then **Yes** (violation), then **Unknown** (uncertainty). Observe compliance, QA and coverage change live.
5. Click **Run deliberate failure test**. The actual `validate()` function rejects a pair missing its negative counterpart.
6. Optionally run `bash run.sh test` in a terminal to demonstrate reproducibility.

## What you must not claim

The repository README says this is a **personal implementation**, not DRDO institutional code or internship measurements. The demo uses **synthetic fixture labels and policies**, no video is generated or judged and **the additional toy classifier does produce training/test scores on synthetic coded images, not pretrained VLM or video benchmark results**. The 648 prompt records are not 648 independent scenes. Scene prompts still need human review before formal evaluation. Show this dashboard as a reproducible software demonstration, not a benchmarking result.

## With actual video evidence later

Use the existing NegationScope workflow: generate a small number of real videos externally, attach them to complete positive/negative pairs via media manifest, extract frames using the optional video dependencies, run a configured vision judge, then `evaluate` and `report`. Record model version, resolution, generation settings, seeds and provenance. Keep results separate from synthetic fixtures.

## Troubleshooting

- `ModuleNotFoundError: negationscope`: run from the repository root with `bash run.sh`.
- Python version error: install Python 3.10 or newer.
- Port in use: `PORT=8766 bash run.sh`.
- Browser does not open automatically: open the printed `127.0.0.1` URL manually.
- `run.sh` on native Windows: use WSL/Git Bash; Python-only fallback needs `PYTHONPATH` configured.
