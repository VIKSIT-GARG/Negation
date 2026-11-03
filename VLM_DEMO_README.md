# NegationScope — tiny multimodal negation demonstrator

This overlay works with the **existing** `VIKSIT-GARG/Negation` repository. It includes the earlier research dashboard plus a new CPU-trainable toy multimodal classifier. It is safe to copy onto the repository root without replacing your existing research modules. The `model/demo_scene_seeds.jsonl` is a portable seed fallback.

## Requirements

- Python 3.10+; Python `numpy` package (`python3 -m pip install numpy`)
- No GPU, no AI service, no videos or API key
- Internet not needed after NumPy is installed

## Run

```bash
git clone https://github.com/VIKSIT-GARG/Negation.git
cd Negation
# Copy the contents of this package here (merge folders)
python3 -m pip install numpy
bash run.sh
# browser: http://127.0.0.1:8765
```

For model-only training: `bash run.sh model`. For tests and dataset validation: `bash run.sh test` (existing repository required for its additional tests). Results go to `runs/toy-vlm/dataset.jsonl`, `model.npz`, `results.json`, and `images/*.svg`.

## What dataset does

- 36 authored scene seeds across 18 categories
- 72 generated artificial images: target object visibly present or absent per scene
- 432 labeled image/text examples: for each image, positive and negative prompts, each expressed in lexical, morphological and syntactic forms
- Balanced MATCH/MISMATCH outcomes; each scene family stays entirely in train, validation, or held-out test
- 288 training, 72 validation and 72 held-out test records
- Label = whether the image contains the object that the text says should be present, or omits the object that text says should be absent

## What is the model?

This is a **deliberately tiny, synthetic VLM-inspired model**, not a pretrained CLIP/BLIP/LLaVA equivalent. It has image patch tokenization, text query-token encoding, deterministic query-to-image softmax attention, and a **real neural two-layer classification head trained with gradient descent** on CPU. Its visual vocabulary is synthetic and hard-coded; only the classifier head learns. It does **not** accept photographs or videos, nor does it test whether a text-to-video generator preserved negation. It measures a simpler *text–image constraint consistency* task.

Because target presence is encoded directly into a simple pixel palette and the classification task is separable, near-perfect scores are expected. They **do not generalize** to real VLM or video metrics.

## Teacher demo

1. Open the dashboard and show the train/validation/test sample counts.
2. Pick a held-out sample. The image displays the target or its absence; the prompt includes 'with'/'without' etc.
3. Click **Run model inference** for a real prediction from trained saved weights.
4. Click **Flip negation and infer**. The image stays the same while text polarity flips, so the model's match prediction should flip.
5. Show the original fixture scoring and dataset integrity validation modules below.

### Transparent explanation

> We do not yet generate videos here. Instead, we isolate one step in the evaluation problem: whether a text–image matching model correctly detects the contradiction between an image and a negative instruction. These images are synthetic and the model has a built-in structured visual codebook. The experiment is reproducible but should not be interpreted as results on a pretrained vision-language model.
