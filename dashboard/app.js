const el=id=>document.getElementById(id);
const pct=n=>(100*n).toFixed(1)+'%';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let catalog=[];
async function get(url){const r=await fetch(url);if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}
async function initialize(){try{
 const [d,ps]=await Promise.all([get('/api/summary'),get('/api/pairs')]);
 for(const [k,v] of Object.entries({records:d.summary.records,pairsCount:d.summary.pairs,scenes:d.summary.scenes,categories:d.summary.categories}))el(k).textContent=v;
 const labels={'perfect':'Perfect fixture','always-yes':'Always-yes fixture','always-no':'Always-no fixture','abstain':'Abstaining fixture'};
 el('comparison').innerHTML=Object.entries(d.fixtures).map(([k,v])=>`<div class="fixture"><h3>${labels[k]}</h3><small>Negation compliance · strict</small><div class="number ${k==='always-yes'?'danger':k==='abstain'?'violet':''}">${pct(v.negation_compliance_strict)}</div><div class="track"><div class="fill" style="width:${100*v.negation_compliance_strict}%"></div></div><small>All evaluated under synthetic policies</small><div class="meta">QA accuracy <b>${pct(v.qa_accuracy_strict)}</b><br>Coverage <b>${pct(v.coverage)}</b><br>Paired success <b>${pct(v.paired_success_rate)}</b></div></div>`).join('');
 el('pipeline').innerHTML=d.pipeline.map(x=>`<li>${esc(x)}</li>`).join('');
 catalog=ps.pairs;
 el('pairSelect').innerHTML=catalog.map((p,i)=>`<option value="${i}">${esc(p.scene_id)} · ${esc(p.category)} · ${esc(p.type)} / ${esc(p.position)}</option>`).join('');
 el('pairSelect').addEventListener('change',showPair);showPair();
 }catch(e){el('comparison').textContent='Unable to load dataset: '+e.message;}}
function showPair(){const p=catalog[+el('pairSelect').value];if(!p)return;el('positivePrompt').textContent=p.positive;el('negativePrompt').textContent=p.negative;const q=p.questions.find(q=>q.id==='target');el('question').textContent=q.text;el('expected').textContent='Reference expected answer: '+q.negative;el('liveResult').className='result empty';el('liveResult').textContent='Choose a response to compute actual strict scoring.';document.querySelectorAll('[data-answer]').forEach(b=>b.classList.remove('selected'));}
document.querySelectorAll('[data-answer]').forEach(b=>b.addEventListener('click',async()=>{const p=catalog[+el('pairSelect').value];if(!p)return;document.querySelectorAll('[data-answer]').forEach(x=>x.classList.toggle('selected',x===b));const r=await fetch('/api/live',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pair_id:p.pair_id,answer:b.dataset.answer})});const d=await r.json();if(!r.ok){el('liveResult').textContent=d.error;return;}el('liveResult').className='result';el('liveResult').innerHTML=`<div><strong>${esc(d.explanation)}</strong></div><div class="metricRow"><span>Target compliance: ${pct(d.target_correct)}</span><span>Pair success: ${pct(d.pair_success)}</span><span>Strict QA: ${pct(d.qa_strict)}</span><span>Coverage: ${pct(d.coverage)}</span></div><p class="hint">${esc(d.notice)}</p>`;}));
el('breakButton').addEventListener('click',async()=>{try{const d=await get('/api/invalid-pair');el('validationResult').textContent=d.status+'\n'+d.error+'\n'+d.why;}catch(e){el('validationResult').textContent=e.message}});
initialize();

// REAL, TRAINED CPU TOY MODEL. Inputs are transparent synthetic icon/patch encodings.
let toySamples=[];
async function bootToy(){try{
 const [info, data] = await Promise.all([get('/api/model-summary'),get('/api/model-samples')]);
 toySamples=data.samples.filter(x=>x.split==='test');
 el('toyStats').innerHTML=`<div><small>EXAMPLES</small><strong>${info.rows}</strong></div><div><small>SYNTHETIC IMAGES</small><strong>${info.images}</strong></div><div><small>HELD-OUT TEST</small><strong>${info.test.n}</strong></div><div><small>TEST MATCH ACCURACY</small><strong>${pct(info.test.accuracy)}</strong></div>`;
 el('toySelect').innerHTML=toySamples.map((r,i)=>`<option value="${i}">${esc(r.scene_id)} · ${esc(r.target)} · ${r.target_present?'object present':'object absent'} · ${r.negated?'NEGATIVE':'POSITIVE'}</option>`).join('');
 el('toySelect').addEventListener('change',showToy); showToy();
 }catch(e){el('toyStats').textContent='Model unavailable: '+e.message;}}
function showToy(){const r=toySamples[+el('toySelect').value];if(!r)return;
 el('toyImage').src='/api/model-image?id='+encodeURIComponent(r.image_id);
 el('toyPrompt').textContent=r.prompt;
 el('toyFacts').textContent=`Ground truth: object ${r.target_present?'PRESENT':'ABSENT'} · expected image–prompt match: ${r.label?'YES':'NO'} · ${r.split.toUpperCase()} split`;
 el('toyResult').textContent='Choose Run model inference to execute the saved trained model.';}
async function tryToy(flip){let r=toySamples[+el('toySelect').value]; if(!r)return;
 const response=await fetch('/api/model-infer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sample_id:r.sample_id,flip_negation:flip})});
 const d=await response.json(); if(!response.ok){el('toyResult').textContent=d.error;return;}
 el('toyResult').innerHTML=`<strong>${d.predicted_match?'MATCH — constraint satisfied':'MISMATCH — constraint violated'}</strong><div class="metricRow"><span>Match score ${pct(d.confidence)}</span><span>Target attention ${pct(d.target_attention)}</span><span>${d.correct?'CORRECT':'INCORRECT'} prediction</span></div><p class="hint">${flip?'The text negation was flipped while the same image was retained. ':''}${esc(d.explanation)}</p>`;
}
el('inferBtn').addEventListener('click',()=>tryToy(false));
el('flipBtn').addEventListener('click',()=>tryToy(true));
bootToy();
