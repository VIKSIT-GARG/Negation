import unittest
from model.toy_vlm import seed_scenes, create_dataset, features, TinyMultimodalMatcher, evaluate
import tempfile
from pathlib import Path
import numpy as np

class TestToyVLM(unittest.TestCase):
    def test_no_leakage(self):
        with tempfile.TemporaryDirectory() as p:
            rows=create_dataset(seed_scenes(),p)
            self.assertEqual(len(rows),432)
            self.assertEqual(len({r['image_id'] for r in rows}),72)
            splits={}
            for r in rows:
                splits.setdefault(r['scene_id'],set()).add(r['split'])
            self.assertTrue(all(len(v)==1 for v in splits.values()))
    def test_model_learns(self):
        with tempfile.TemporaryDirectory() as p:
            rows=create_dataset(seed_scenes(),p)
            train=[r for r in rows if r['split']=='train']
            test=[r for r in rows if r['split']=='test']
            m=TinyMultimodalMatcher()
            m.train(np.stack([features(r,36) for r in train]), np.array([r['label'] for r in train]))
            self.assertGreaterEqual(evaluate(m,test)['accuracy'],0.95)
    def test_flip_negation_changes_label(self):
        with tempfile.TemporaryDirectory() as p:
            row=create_dataset(seed_scenes()[:1],p)[0]
            altered=dict(row,negated=not row['negated'])
            altered['label']=int(altered['target_present'] != altered['negated'])
            self.assertNotEqual(row['label'],altered['label'])

if __name__=='__main__': unittest.main()
