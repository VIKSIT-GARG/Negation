"""Offline localhost research demonstrator. Synthetic fixture data only.

No external dependencies, API keys, model downloads or network services.
All scoring uses the actual negationscope.dataset and negationscope.metrics modules.
"""
import argparse
import copy
import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from model.toy_vlm import train_and_export, infer_sample, OUTPUT as MODEL_OUTPUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from negationscope.dataset import construct, validate  # noqa: E402
from negationscope.io import read_jsonl  # noqa: E402
from negationscope.metrics import evaluate  # noqa: E402

SEEDS = ROOT / "data" / "scene_seeds.jsonl"
MODEL_ROWS = []
MODEL_REPORT = {}

def initialize_model():
    global MODEL_ROWS, MODEL_REPORT
    if not (MODEL_OUTPUT / "results.json").exists():
        train_and_export()
    MODEL_REPORT = json.loads((MODEL_OUTPUT / "results.json").read_text())
    MODEL_ROWS = [json.loads(line) for line in (MODEL_OUTPUT / "dataset.jsonl").read_text().splitlines() if line.strip()]

STATIC = Path(__file__).resolve().parent
ALL = construct(read_jsonl(SEEDS), seed=42)
SUMMARY = validate(ALL)
PAIRS = {}
for row in ALL:
    PAIRS.setdefault(row['pair_id'], {})[row['polarity']] = row


def _answer_label(value):
    return 'Unknown' if value is None else 'Yes' if value else 'No'


def _predictions(rows, policy):
    output = []
    for row in rows:
        for q in row['questions']:
            if policy == 'perfect':
                answer = q['expected']
            elif policy == 'always-yes':
                answer = True
            elif policy == 'abstain':
                answer = None
            elif policy == 'always-no':
                answer = False
            else:
                raise ValueError('invalid fixture')
            output.append({'model': 'synthetic-' + policy, 'judge': 'fixture-not-a-vlm',
                           'sample_id': row['sample_id'], 'question_id': q['question_id'],
                           'answer': answer, 'synthetic_fixture': True})
    return output


def fixture_metrics(policy):
    # Full generated dataset (not real model inference)
    results = evaluate(ALL, _predictions(ALL, policy), seed=42)
    m = results['models']['synthetic-' + policy]
    return {k: m[k] for k in ('qa_accuracy_strict', 'negation_compliance_strict',
                              'coverage', 'paired_success_rate', 'forbidden_presence_rate',
                              'negative_target_unknown_rate', 'negative_minus_positive_qa')}


def metrics_endpoint():
    policies = ('perfect', 'always-yes', 'always-no', 'abstain')
    return {'notice': 'SYNTHETIC FIXTURES ONLY — NOT MEASURED MODEL PERFORMANCE',
            'summary': {'records': SUMMARY['samples'], 'pairs': SUMMARY['pairs'],
                        'scenes': SUMMARY['scenes'], 'categories': len(SUMMARY['categories']),
                        'review_status': SUMMARY['review_status']},
            'fixtures': {policy: fixture_metrics(policy) for policy in policies},
            'categories': SUMMARY['categories'], 'splits': SUMMARY['splits'],
            'pipeline': ['Authored scene seeds', 'Matched prompt construction', 'Dataset validation',
                         'External video generation (not run here)', 'Frame sampling (requires videos)',
                         'Blind VLM judging (requires media/model)', 'Strict scoring + reports']}


def catalog():
    return [{'pair_id': pair_id, 'scene_id': pair['positive']['scene_id'],
             'category': pair['positive']['category'], 'type': pair['positive']['negation_type'],
             'position': pair['positive']['position'],
             'positive': pair['positive']['prompt'], 'negative': pair['negative']['prompt'],
             'questions': [{'id': q['question_id'], 'text': q['text'],
                            'positive': _answer_label(q['expected']),
                            'negative': _answer_label(next(x for x in pair['negative']['questions'] if x['question_id'] == q['question_id'])['expected'])}
                           for q in pair['positive']['questions']]}
            for pair_id, pair in list(PAIRS.items())[:70]]


def run_live(body):
    pair_id = body.get('pair_id')
    if not isinstance(pair_id, str) or pair_id not in PAIRS:
        raise ValueError('Choose a valid pair')
    answer = body.get('answer')
    if answer not in ('yes', 'no', 'unknown'):
        raise ValueError('Answer must be yes, no, or unknown')
    pair = PAIRS[pair_id]
    rows = [pair['positive'], pair['negative']]
    preds = _predictions(rows, 'perfect')
    for p in preds:
        if p['sample_id'] == pair['negative']['sample_id'] and p['question_id'] == 'target':
            p['answer'] = {'yes': True, 'no': False, 'unknown': None}[answer]
    metric = evaluate(rows, preds, seed=42)['models']['synthetic-perfect']
    negative_q = next(q for q in pair['negative']['questions'] if q['question_id'] == 'target')
    return {'notice': 'SIMULATED HUMAN/JUDGE ANSWER — NO VIDEO WAS ANALYZED',
            'pair_id': pair_id, 'positive': pair['positive']['prompt'], 'negative': pair['negative']['prompt'],
            'question': negative_q['text'], 'expected': _answer_label(negative_q['expected']),
            'supplied': answer.capitalize(), 'target_correct': metric['negation_compliance_strict'],
            'pair_success': metric['paired_success_rate'], 'qa_strict': metric['qa_accuracy_strict'],
            'coverage': metric['coverage'],
            'explanation': ('Target absence confirmed under the synthetic answer.' if answer == 'no'
                            else 'The excluded object was reported present: constraint violated.' if answer == 'yes'
                            else 'Uncertainty is preserved, not counted as success.')}


def test_invalid_pair():
    # Actual validator demonstration: remove one counterpart and catch expected failure.
    rows = copy.deepcopy([PAIRS[next(iter(PAIRS))]['positive']])
    try:
        validate(rows)
    except ValueError as exc:
        return {'status': 'PASS — invalid dataset correctly rejected', 'error': str(exc),
                'why': 'One missing polarity invalidates a matched pair.'}
    return {'status': 'FAIL — invalid dataset accepted'}


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/model-summary':
            return self.send_json(MODEL_REPORT)
        if path == '/api/model-samples':
            return self.send_json({'samples': MODEL_ROWS[::3]})
        if path == '/api/model-image':
            image_id = parse_qs(urlparse(self.path).query).get('id',[''])[0]
            if image_id not in {r['image_id'] for r in MODEL_ROWS}:
                return self.send_json({'error': 'image not found'},404)
            raw=(MODEL_OUTPUT/'images'/f'{image_id}.svg').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','image/svg+xml')
            self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'")
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers(); self.wfile.write(raw); return
        if path == '/api/summary':
            return self.send_json(metrics_endpoint())
        if path == '/api/pairs':
            return self.send_json({'pairs': catalog()})
        if path == '/api/invalid-pair':
            return self.send_json(test_invalid_pair())
        if path in ('/', '/index.html', '/styles.css', '/app.js'):
            target = STATIC / ('index.html' if path == '/' else path.lstrip('/'))
            content = target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(target.name)[0] or 'text/plain')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(content)
            return
        self.send_json({'error': 'not found'}, 404)

    def do_POST(self):
        route = urlparse(self.path).path
        if route not in ('/api/live','/api/model-infer'):
            return self.send_json({'error': 'not found'}, 404)
        try:
            n = int(self.headers.get('Content-Length', '0'))
            if n < 1 or n > 4096:
                raise ValueError('Invalid request length')
            body = json.loads(self.rfile.read(n))
            if not isinstance(body, dict):
                raise ValueError('Expected an object')
            if route == "/api/model-infer":
                sample_id=body.get("sample_id")
                if not isinstance(sample_id,str): raise ValueError("Invalid sample ID")
                row=next((r for r in MODEL_ROWS if r["sample_id"]==sample_id),None)
                if row is None: raise ValueError("Sample not found")
                if body.get("flip_negation") is True:
                    row=dict(row); row["negated"]=not row["negated"]; row["label"]=int(row["target_present"] != row["negated"])
                self.send_json({**infer_sample(row),"negated":row["negated"],"target_present":row["target_present"],"image_id":row["image_id"]})
            else:
                self.send_json(run_live(body))
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({'error': str(exc)}, 400)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8765)
    args = p.parse_args()
    initialize_model()
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        print(f'NegationScope demo: http://127.0.0.1:{args.port}', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
