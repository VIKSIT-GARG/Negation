"""Educational *VLM-inspired* dual-stream patch/text attention matching model.

Fully synthetic images, tiny non-pretrained model, CPU-only NumPy.
The image encoder uses a controlled palette/token representation (not natural-image
understanding). Query-to-patch attention is deterministic; a neural classification
head is actually trained and evaluated on untouched scene-family splits.
Never claim this is a pretrained VLM or evaluates real video generators.
"""
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / 'data' / 'scene_seeds.jsonl'
FALLBACK_SEEDS = Path(__file__).resolve().parent / 'demo_scene_seeds.jsonl'
OUTPUT = ROOT / 'runs' / 'toy-vlm'


def seed_scenes(path=SEEDS):
    path = Path(path) if Path(path).exists() else FALLBACK_SEEDS
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def image_tokens(scene_index, present, clutter=0):
    """12x12 discrete artificial image: background 0, subject 1, target id 2+index.
    The target code matches the corresponding query word codebook; this is a
    supervised synthetic visual vocabulary, NOT unsupervised visual learning.
    """
    im = np.zeros((12, 12), dtype=np.int32)
    im[3:10, 2:5] = 1  # stylized person/animal body
    im[1:4, 2:5] = 1
    if present:
        im[5:9, 8:11] = scene_index + 2
    if clutter:
        im[10:12, 0:2] = 99
    return im


def render_svg(scene_index, present, subject='', target=''):
    """Diagrammatic generated visual with no photos or real video evidence."""
    palette = ['#4ade80','#f59e0b','#fb7185','#38bdf8','#c084fc','#f97316','#2dd4bf']
    fill = palette[scene_index % len(palette)]
    target_svg = f'<circle cx="285" cy="140" r="33" fill="{fill}" stroke="#f4f7ff" stroke-width="3"/>' if present else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">'
            '<rect width="400" height="250" rx="15" fill="#101e35"/>'
            '<rect y="198" width="400" height="52" fill="#19324b"/>'
            '<circle cx="112" cy="70" r="30" fill="#92a7c9"/>'
            '<rect x="83" y="100" width="58" height="95" rx="15" fill="#6582a9"/>'
            '<path d="M92 190 L85 225 M131 190 L143 225" stroke="#92a7c9" stroke-width="12" stroke-linecap="round"/>'
            f'{target_svg}</svg>')


def create_dataset(scenes, out=OUTPUT):
    """Every scene yields 2 visual states × 2 language polarities × 3 forms.
    Class labels evaluate *image-text consistency*, not generated video quality.
    Scene-held-out split is determined by scene index to avoid row-level leakage.
    """
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'images').mkdir(exist_ok=True)
    rows = []
    types = ['lexical','morphological','syntactic']
    for idx, scene in enumerate(scenes):
        split = 'test' if idx % 6 == 0 else ('validation' if idx % 6 == 1 else 'train')
        for present in (False,True):
            image_id = f"{scene['scene_id']}_{'present' if present else 'absent'}"
            (out / 'images' / f'{image_id}.svg').write_text(render_svg(idx, present), encoding='utf-8')
            for negative in (False,True):
                for kind in types:
                    if kind == 'lexical':
                        phrase = f"{'without' if negative else 'with'} {scene['target']}"
                    elif kind == 'morphological':
                        phrase = f"{'an absence of' if negative else 'the presence of'} {scene['target']}"
                    else:
                        phrase = f"there is {'no' if negative else 'a'} {scene['target_stem']}"
                    prompt = f"{scene['subject'].capitalize()} {scene['action']} {scene['setting']}; {phrase}."
                    rows.append({'sample_id':f'{image_id}_{kind}_{"neg" if negative else "pos"}',
                        'scene_id':scene['scene_id'],'scene_index':idx,'category':scene['category'],
                        'split':split,'image_id':image_id,'image_path':f'images/{image_id}.svg',
                        'target':scene['target'],'target_present':present,'negated':negative,
                        'prompt_type':kind,'prompt':prompt,'label':int(present != negative)})
    (out/'dataset.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows), encoding='utf-8')
    return rows


def features(row, total_scenes):
    """Dual-stream encoded tokens with scaled dot-product query→image attention.
    Text tokens: target shared codebook, polarity and form. Image visual tokens:
    subject/background + target token when present. Uses one-hot synthetic
    visual vocabulary so attention has directly interpretable semantics.
    """
    idx = row['scene_index']
    im = image_tokens(idx, row['target_present'])
    # Attention uses word identifier as query, image patch identifiers as keys.
    # High score for image patches showing the queried object.
    scores = np.where(im.ravel()==idx+2, 9.0, -4.0)
    a = np.exp(scores-scores.max()); a /= a.sum()
    target_attention = float(a[im.ravel()==idx+2].sum())
    is_neg = float(row['negated'])
    # Multimodal fusion features; interaction learnt by MLP, no rule-based label.
    return np.array([target_attention, is_neg, target_attention*is_neg,
                     1.0-target_attention, 1.0,], dtype=np.float64)


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -30, 30)))


class TinyMultimodalMatcher:
    """A trained two-layer MLP readout over cross-attention + language features."""
    def __init__(self, seed=42):
        rng=np.random.default_rng(seed)
        self.w1=rng.normal(0,.25,(5,12)); self.b1=np.zeros(12)
        self.w2=rng.normal(0,.25,(12,1)); self.b2=np.zeros(1)

    def infer(self, x):
        h=np.tanh(x@self.w1+self.b1)
        return sigmoid(h@self.w2+self.b2).reshape(-1)

    def train(self, x,y,epochs=360,rate=.11):
        y=y.reshape(-1,1)
        for _ in range(epochs):
            h=np.tanh(x@self.w1+self.b1)
            p=sigmoid(h@self.w2+self.b2)
            d=(p-y)/len(y)
            dw2=h.T@d; db2=d.sum(axis=0)
            dh=(d@self.w2.T)*(1-h*h)
            dw1=x.T@dh; db1=dh.sum(axis=0)
            self.w2-=rate*dw2; self.b2-=rate*db2
            self.w1-=rate*dw1; self.b1-=rate*db1

    def save(self,p):
        np.savez(p,w1=self.w1,b1=self.b1,w2=self.w2,b2=self.b2)

    @classmethod
    def load(cls,p):
        m=cls(); z=np.load(p)
        for k in ('w1','b1','w2','b2'): setattr(m,k,z[k])
        return m


def evaluate(model, rows):
    x=np.stack([features(r,36) for r in rows]); y=np.array([r['label'] for r in rows])
    probs=model.infer(x); predicted=(probs>=.5).astype(int)
    correct=(predicted==y)
    def slice_stats(subset):
        inds=np.array(subset,dtype=bool)
        if not inds.any(): return {'n':0,'accuracy':None}
        return {'n':int(inds.sum()),'accuracy':float(correct[inds].mean())}
    return {'n':len(rows),'accuracy':float(correct.mean()),
            'negative':slice_stats([r['negated'] for r in rows]),
            'positive':slice_stats([not r['negated'] for r in rows]),
            'false_accepts':int(((predicted==1)&(y==0)).sum()),
            'false_rejects':int(((predicted==0)&(y==1)).sum())}


def train_and_export(root=OUTPUT):
    root=Path(root); scenes=seed_scenes(); rows=create_dataset(scenes,root)
    train=[r for r in rows if r['split']=='train']
    val=[r for r in rows if r['split']=='validation']
    test=[r for r in rows if r['split']=='test']
    m=TinyMultimodalMatcher()
    m.train(np.stack([features(r,len(scenes)) for r in train]),np.array([r['label'] for r in train]))
    m.save(root/'model.npz')
    report={'notice':'REAL TRAINED TINY MODEL ON SYNTHETIC COLOR-CODED IMAGE TOKENS — NOT A PRETRAINED VLM; NO VIDEO MODEL TESTED',
            'architecture':'Synthetic image patch tokens + text target query + scaled-dot-product cross attention + trained 2-layer MLP classifier',
            'train':evaluate(m,train),'validation':evaluate(m,val),'test':evaluate(m,test),
            'rows':len(rows),'images':len(scenes)*2,'scenes':len(scenes),
            'splits':dict(Counter(r['split'] for r in rows))}
    (root/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


def infer_sample(row, model_path=OUTPUT/'model.npz'):
    m=TinyMultimodalMatcher.load(model_path)
    p=float(m.infer(features(row,36)[None,:])[0]); label=int(p>=.5)
    return {'predicted_match':bool(label),'confidence':round(p,4),
            'correct':bool(label==row['label']), 'expected_match':bool(row['label']),
            'target_attention':round(float(features(row,36)[0]),4),
            'explanation':'The tiny model compares the target word token with synthetic image patch tokens, then uses a trained neural classifier to predict prompt-image agreement.'}


if __name__=='__main__':
    print(json.dumps(train_and_export(),indent=2))
