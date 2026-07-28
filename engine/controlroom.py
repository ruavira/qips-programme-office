#!/usr/bin/env python3
"""Generate the CCC control room — one page showing the whole programme."""
import os, sys, html, re
sys.path.insert(0, os.path.dirname(__file__))
from workstreams import WORKSTREAMS, DIRECTORATES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ccc", "control-room.html")

facts = open(os.path.join(ROOT, "canon/facts.yaml"), encoding="utf-8").read()
n_appr = facts.count("status: APPROVED")
n_prop = facts.count("status: PROPOSED")
oq = open(os.path.join(ROOT, "canon/open-questions.yaml"), encoding="utf-8").read()
questions = []
for blk in re.split(r"\n  - id: ", oq)[1:]:
    qid = blk.split("\n")[0].strip()
    q = re.search(r'question: "(.*?)"', blk, re.S)
    owner = re.search(r"owner: (\w+)", blk)
    blocking = "blocking: true" in blk
    blocks = re.search(r"blocks: \[(.*?)\]", blk)
    due = re.search(r"due: ([\d-]+)", blk)
    note = re.search(r'note: "(.*?)"', blk, re.S)
    questions.append(dict(id=qid, q=q.group(1) if q else "", owner=owner.group(1) if owner else "",
                          blocking=blocking, blocks=blocks.group(1) if blocks else "",
                          due=due.group(1) if due else "", note=note.group(1) if note else ""))

DCOL = {"D1": "#0F5257", "D2": "#1D6F5C", "D3": "#3B5BA5", "D4": "#8A5A00"}
SCOPE_LABEL = {"NOW": "Cohort 1", "NEXT": "Cohort 2", "LATER": "Later"}

def esc(s): return html.escape(str(s))

# blocking map
blocks_map = {}
for ws in WORKSTREAMS:
    for dep in ws["depends_on"]:
        blocks_map.setdefault(dep, []).append(ws["id"])

cards = ""
for dk, (dname, ddesc) in DIRECTORATES.items():
    ws_list = [w for w in WORKSTREAMS if w["d"] == dk]
    cards += f"""<section class="dir" data-dir="{dk}">
      <div class="dir-head" style="--dc:{DCOL[dk]}">
        <span class="dk">{dk}</span>
        <h2>{esc(dname)}</h2>
        <p>{esc(ddesc)}</p>
      </div>
      <div class="grid">"""
    for w in ws_list:
        qs = [q for q in questions if q["owner"] == w["id"]]
        blocking_q = [q for q in qs if q["blocking"]]
        deps = ", ".join(w["depends_on"]) if w["depends_on"] else "—"
        blocks = ", ".join(blocks_map.get(w["id"], [])) or "—"
        flag = "blocked" if blocking_q else ("ready" if not w["depends_on"] else "waiting")
        flabel = {"blocked": "Blocking question open", "ready": "Can start now", "waiting": "Waits on upstream"}[flag]
        cards += f"""
        <article class="ws {flag}" data-scope="{w['cohort1']}" style="--dc:{DCOL[dk]}" tabindex="0">
          <header>
            <span class="wid">{w['id']}</span>
            <span class="scope s-{w['cohort1']}">{SCOPE_LABEL[w['cohort1']]}</span>
          </header>
          <h3>{esc(w['name'])}</h3>
          <p class="q">{esc(w['owner_question'])}</p>
          <div class="flag f-{flag}">{flabel}</div>
          <details>
            <summary>What it must produce · dependencies · benchmarks</summary>
            <div class="det">
              <h4>Produces</h4><ul>{''.join(f'<li>{esc(o)}</li>' for o in w['outputs'])}</ul>
              <h4>Research lenses</h4><ul>{''.join(f'<li>{esc(l)}</li>' for l in w['lenses'])}</ul>
              <h4>Benchmarks against</h4><p class="bm">{esc(' · '.join(w['benchmarks']))}</p>
              <h4>Dependencies</h4><p class="bm">Waits on: <b>{deps}</b> &nbsp;·&nbsp; Blocks: <b>{blocks}</b></p>
              <h4>Standing note</h4><p class="note">{esc(w['note'])}</p>
              {'<h4>Open questions it owns</h4><ul>' + ''.join(f"<li>{'<b>BLOCKING</b> · ' if q['blocking'] else ''}{esc(q['q'])} <span class=due>due {esc(q['due'])}</span></li>" for q in qs) + '</ul>' if qs else ''}
            </div>
          </details>
        </article>"""
    cards += "</div></section>"

blockers = "".join(f"""<tr class="{'blk' if q['blocking'] else ''}">
  <td class="qid">{esc(q['id'])}</td><td>{esc(q['q'])}</td>
  <td class="own">{esc(q['owner'])}</td><td class="own">{esc(q['blocks'])}</td>
  <td class="due">{esc(q['due'])}</td></tr>""" for q in sorted(questions, key=lambda x: (not x["blocking"], x["due"])))

now = [w['id'] for w in WORKSTREAMS if w['cohort1'] == 'NOW']
nxt = [w['id'] for w in WORKSTREAMS if w['cohort1'] == 'NEXT']

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>QIPS Programme Office — control room</title><style>
*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;color:#14201F;background:#F5F8F8}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 20px 90px}}
header.top{{background:linear-gradient(150deg,#0F5257,#0B3A3E 55%,#082A2D);color:#fff;padding:40px 20px 34px}}
header.top .wrap{{padding-bottom:0}}
.kicker{{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#D9A441;font-weight:700}}
h1{{font-size:29px;margin:9px 0 8px;line-height:1.15}}
header.top p{{margin:0;color:#B7CBC9;max-width:70ch;font-size:14.5px}}
.stats{{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}}
.stat{{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.16);border-radius:9px;padding:9px 14px;min-width:96px}}
.stat b{{display:block;font-size:21px;line-height:1.1;color:#F0D9A8}}
.stat span{{font-size:10.5px;text-transform:uppercase;letter-spacing:.09em;color:#9FBAB8}}
.bar{{position:sticky;top:0;z-index:9;background:rgba(245,248,248,.94);backdrop-filter:blur(7px);border-bottom:1px solid #DFE7E6;padding:11px 0;margin-bottom:22px}}
.bar .wrap{{padding-bottom:0;display:flex;gap:7px;flex-wrap:wrap;align-items:center}}
button.f{{border:1px solid #C9D6D5;background:#fff;border-radius:20px;padding:5px 13px;font:inherit;font-size:12.5px;cursor:pointer;color:#3A4746}}
button.f.on{{background:#0F5257;color:#fff;border-color:#0F5257}}
.bar em{{font-style:normal;font-size:12px;color:#7C8A88;margin-right:5px}}
.dir-head{{margin:34px 0 14px;padding-left:13px;border-left:4px solid var(--dc)}}
.dir-head .dk{{font-size:10.5px;letter-spacing:.16em;font-weight:800;color:var(--dc)}}
.dir-head h2{{margin:2px 0 3px;font-size:20px}}
.dir-head p{{margin:0;color:#6B7A78;font-size:13.5px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:13px}}
.ws{{background:#fff;border:1px solid #E2EAE9;border-top:3px solid var(--dc);border-radius:11px;padding:15px 17px;transition:box-shadow .15s}}
.ws:hover,.ws:focus{{box-shadow:0 3px 16px rgba(15,82,87,.11);outline:none}}
.ws header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px}}
.wid{{font-size:11.5px;font-weight:800;letter-spacing:.09em;color:var(--dc)}}
.scope{{font-size:10px;text-transform:uppercase;letter-spacing:.08em;padding:2px 8px;border-radius:11px;font-weight:700}}
.s-NOW{{background:#0F5257;color:#fff}} .s-NEXT{{background:#E9EFEE;color:#5A6968}} .s-LATER{{background:#F3F5F5;color:#93A2A0}}
.ws h3{{margin:0 0 7px;font-size:16px;line-height:1.28}}
.q{{margin:0 0 11px;font-size:13.5px;color:#4C5B59;font-style:italic}}
.flag{{font-size:11.5px;font-weight:700;padding:4px 9px;border-radius:6px;display:inline-block}}
.f-blocked{{background:#FDECEC;color:#9B2C2C}} .f-ready{{background:#EAF5EE;color:#1D6F4C}} .f-waiting{{background:#F1F4F4;color:#5A6968}}
details{{margin-top:11px;border-top:1px solid #EEF2F2;padding-top:9px}}
summary{{cursor:pointer;font-size:12.5px;color:#0F5257;font-weight:600;list-style:none}}
summary::-webkit-details-marker{{display:none}}
summary::before{{content:"▸ ";color:#8CA09E}}
details[open] summary::before{{content:"▾ "}}
.det{{font-size:12.8px;color:#41504E;padding-top:6px}}
.det h4{{margin:11px 0 4px;font-size:10.5px;text-transform:uppercase;letter-spacing:.1em;color:#8494 92;color:#849492}}
.det ul{{margin:0;padding-left:17px}} .det li{{margin-bottom:3px}}
.bm,.note{{margin:0;color:#5C6B69}} .note{{font-style:italic}}
.due{{color:#9B2C2C;font-size:11.5px}}
h2.sec{{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#6B7A78;margin:44px 0 12px;font-weight:800}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #E2EAE9;border-radius:11px;overflow:hidden;font-size:13px}}
th,td{{padding:9px 11px;text-align:left;border-bottom:1px solid #EFF3F3;vertical-align:top}}
thead th{{background:#F0F5F4;font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:#5A6968}}
tr.blk td{{background:#FEF7F7}}
.qid{{font-weight:800;color:#0F5257;white-space:nowrap}}
.own{{color:#6B7A78;white-space:nowrap;font-size:12px}}
td.due{{white-space:nowrap;font-weight:600}}
.gate{{background:#0F5257;color:#fff;border-radius:12px;padding:24px 26px;margin-top:20px}}
.gate h3{{margin:0 0 9px;color:#D9A441;font-size:17px}}
.gate p{{margin:0 0 9px;color:#D5E4E2;font-size:14px}}
.gate .verds{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:11px;margin-top:15px}}
.gate .v{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:9px;padding:11px 13px}}
.gate .v b{{display:block;color:#F0D9A8;font-size:12.5px;letter-spacing:.06em;margin-bottom:3px}}
.gate .v span{{font-size:12.5px;color:#CADCDA}}
.road{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:13px}}
.road .c{{background:#fff;border:1px solid #E2EAE9;border-radius:11px;padding:16px 18px}}
.road .c b{{display:block;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#0F5257;margin-bottom:5px}}
.road .c p{{margin:0 0 8px;font-size:13px;color:#5C6B69}}
.road .c code{{font-size:11.5px;color:#41504E;background:#F2F6F5;padding:1px 5px;border-radius:4px;line-height:2}}
footer{{margin-top:44px;padding-top:16px;border-top:1px solid #DCE4E3;color:#7C8A88;font-size:12.5px}}
.hidden{{display:none !important}}
@media(max-width:640px){{h1{{font-size:22px}} .grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header class="top"><div class="wrap">
<div class="kicker">Central Coordinating Committee</div>
<h1>QIPS Programme Office — control room</h1>
<p>Seventeen workstreams, four directorates, one committee. Everything between them runs without a human in it. The committee's only job is to decide — and to be the only route by which anything becomes true.</p>
<div class="stats">
  <div class="stat"><b>{len(WORKSTREAMS)}</b><span>Workstreams</span></div>
  <div class="stat"><b>{n_appr}</b><span>Facts in canon</span></div>
  <div class="stat"><b>{n_prop}</b><span>Awaiting CCC</span></div>
  <div class="stat"><b>{sum(1 for q in questions if q['blocking'])}</b><span>Blocking questions</span></div>
  <div class="stat"><b>{len(now)}</b><span>In cohort 1</span></div>
</div>
</div></header>
<div class="bar"><div class="wrap">
  <em>Show</em>
  <button class="f on" data-f="all">All</button>
  <button class="f" data-f="NOW">Cohort 1 only</button>
  <button class="f" data-f="blocked">Blocked</button>
  <button class="f" data-f="ready">Can start now</button>
  <button class="f" data-f="expand">Expand all</button>
</div></div>
<div class="wrap">
{cards}

<h2 class="sec">Blocking questions — nothing ships until these close</h2>
<table><thead><tr><th>Id</th><th>Question</th><th>Owner</th><th>Blocks</th><th>Due</th></tr></thead>
<tbody>{blockers}</tbody></table>

<h2 class="sec">The gate</h2>
<div class="gate">
  <h3>The committee is the only human in the system</h3>
  <p>It never sees research. It sees a decision dossier in one fixed shape, carrying a benchmark table against named comparators, a council verdict, and a passed adversarial verification. A dossier missing any of those is returned unread — not because the content is wrong, but because accepting it once teaches the system that the gates are optional.</p>
  <p>Cap a cycle at three workstreams. The binding constraint is not compute, it is committee attention. A committee that rubber-stamps because it is overwhelmed is worse than no committee.</p>
  <div class="verds">
    <div class="v"><b>APPROVE</b><span>The facts become canon. Every dependent workstream wakes.</span></div>
    <div class="v"><b>AMEND</b><span>Approved with a named change, attributed to the committee.</span></div>
    <div class="v"><b>REJECT</b><span>With a stated reason — written back into the brief as a standing constraint. A rejection without a reason is the one thing that breaks the loop.</span></div>
    <div class="v"><b>DEFER</b><span>With a named condition and a date. Deferral is a decision and is minuted.</span></div>
  </div>
</div>

<h2 class="sec">What ships when</h2>
<div class="road">
  <div class="c"><b>Cohort 1 · January 2027</b><p>Prove the monthly cycle and the observership. {len(now)} workstreams.</p><code>{' '.join(now)}</code></div>
  <div class="c"><b>Cohort 2 · 2028</b><p>Compound the credential: alumni network, coach pipeline grown from graduates, published outcomes.</p><code>{' '.join(nxt) if nxt else '—'}</code></div>
  <div class="c"><b>Later</b><p>Regional centres qualifying their own host sites under the same standard. An advanced tier above the foundation programme, with a credential ladder between them. External evaluation of the programme itself, on the terms it teaches participants to accept.</p></div>
</div>

<footer>Generated 28 July 2026 from <code>engine/workstreams.py</code> and <code>canon/</code>. Regenerate with <code>python3 engine/controlroom.py</code> after any CCC sitting — this page is a view, never a source.</footer>
</div>
<script>
const btns=[...document.querySelectorAll('button.f')];
btns.forEach(b=>b.addEventListener('click',()=>{{
  const f=b.dataset.f;
  if(f==='expand'){{
    const any=[...document.querySelectorAll('.ws details')].some(d=>!d.open);
    document.querySelectorAll('.ws details').forEach(d=>d.open=any);
    b.textContent=any?'Collapse all':'Expand all'; return;
  }}
  btns.filter(x=>x.dataset.f!=='expand').forEach(x=>x.classList.toggle('on',x===b));
  document.querySelectorAll('.ws').forEach(w=>{{
    const show = f==='all' || (f==='NOW'&&w.dataset.scope==='NOW') || (f!=='NOW'&&w.classList.contains(f));
    w.classList.toggle('hidden',!show);
  }});
  document.querySelectorAll('.dir').forEach(d=>{{
    d.classList.toggle('hidden', ![...d.querySelectorAll('.ws')].some(w=>!w.classList.contains('hidden')));
  }});
}}));
</script></body></html>"""

doc = "\n".join(line.rstrip() for line in doc.splitlines()) + "\n"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(doc)
print("control room:", OUT, len(doc), "bytes")
