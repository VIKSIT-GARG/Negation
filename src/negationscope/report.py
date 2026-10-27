"""Portable HTML report with escaped model names and no external assets."""
from html import escape
from pathlib import Path


def render_report(report, output):
    rows = []
    for name, model in report["models"].items():
        rows.append("<tr><th>" + escape(name) + "</th>" + "".join(f"<td>{model[key]:.1%}</td>" for key in
            ("coverage", "qa_accuracy_strict", "negation_compliance_strict", "paired_success_rate", "negative_minus_positive_qa")) + "</tr>")
    details = []
    for name, model in report["models"].items():
        groups = "".join(f"<tr><td>{escape(k)}</td><td>{v['n']}</td><td>{v['qa_accuracy_strict']:.1%}</td></tr>" for k, v in model["groups"].items())
        details.append(f"<h2>{escape(name)}</h2><table><tr><th>Condition</th><th>Samples</th><th>Strict QA</th></tr>{groups}</table>")
    title = "Synthetic fixture demonstration" if report.get("synthetic_fixture") else "Evaluation report"
    html = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NegationScope report</title><style>body{font:16px system-ui;background:#0d1525;color:#e6edf8;max-width:1100px;margin:50px auto;padding:24px}h1{font-size:42px}p{color:#b7c5db;line-height:1.6}table{width:100%;border-collapse:collapse;margin:24px 0}td,th{text-align:left;padding:14px;border-bottom:1px solid #31415c}th{color:#8ad7c4}h2{margin-top:48px}caption{text-align:left}</style>"""
    html += f"<h1>NegationScope</h1><p>{escape(title)} · Viksit Garg</p>"
    html += "<p>Unknown and missing answers count as failures in strict metrics. Gap = negative QA minus positive QA. Video quality is evaluated separately. Sampled frames cannot establish absence across every unsampled moment.</p>"
    html += "<table><tr><th>System</th><th>Coverage</th><th>Strict QA</th><th>Negation</th><th>Paired success</th><th>QA gap</th></tr>" + "".join(rows) + "</table>" + "".join(details) + "</html>"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html, encoding="utf-8")
