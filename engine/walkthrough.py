#!/usr/bin/env python3
"""Render the CCC design walkthrough as one self-contained HTML file.

WHY A SINGLE FILE
-----------------
The reviewer opens it in a browser. No login, no install, no server, works on a
phone, works offline, survives a dropped connection mid-session. It commits the
programme to no platform — the hosting question stays open, which matters while
Base44 may or may not be the final destination.

It does NOT use localStorage or any browser storage API. Progress is held in
memory and saved by an explicit download, and resumed by loading that file back.
That is a real constraint on the reviewer (close the tab, lose unsaved work) and
the page says so plainly rather than pretending otherwise.

WHAT IT IS NOT
--------------
Not a mockup. Every stop is generated from engine/decision_interview.py, which is
generated from the repository. The narrative spine is data in
engine/schemas/walkthrough-journey.yaml. Nothing here is authored twice, so
nothing here can drift from the build.

Usage:
    python3 engine/walkthrough.py --out walkthrough.html
    python3 engine/walkthrough.py --check
    python3 engine/walkthrough.py --self-test
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
JOURNEY_PATH = ROOT / "engine/schemas/walkthrough-journey.yaml"

sys.path.insert(0, str(ROOT / "engine"))
import decision_interview as di  # noqa: E402


class WalkthroughError(Exception):
    """The walkthrough cannot be built. Nothing is emitted."""


def load_journey() -> dict[str, Any]:
    if not JOURNEY_PATH.is_file():
        raise WalkthroughError(f"{JOURNEY_PATH.relative_to(ROOT)} does not exist.")
    return yaml.safe_load(JOURNEY_PATH.read_text(encoding="utf-8"))


def _anchor_key(station: dict[str, Any]) -> set[str]:
    """The names an act may use to anchor a station: its id, and its fact id."""
    keys = {station["id"]}
    tail = station["source"].split("::")[-1]
    if tail:
        keys.add(tail)
    return keys


def anchor(stations: list[dict[str, Any]], journey: dict[str, Any]) -> tuple[list[dict], list[str]]:
    """Place every station in exactly one act.

    Anything the spine has not placed lands in the catch-all act and is reported.
    An unplaced item is not dropped — an item the reviewer never reaches is an
    item they were never shown, which is the failure this whole design exists to
    prevent.
    """
    acts = [dict(act, stops=[]) for act in journey["acts"]]
    catch_all = next((a for a in acts if a.get("catch_all")), acts[-1])

    placed: set[str] = set()
    duplicates: list[str] = []

    for act in acts:
        wanted = set(act.get("anchors") or [])
        if not wanted:
            continue
        for station in stations:
            if not (_anchor_key(station) & wanted):
                continue
            if station["id"] in placed:
                duplicates.append(
                    f"{station['id']} is anchored in more than one act; the reviewer would "
                    "meet it twice and could answer it differently each time."
                )
                continue
            act["stops"].append(station)
            placed.add(station["id"])

    unplaced = [s for s in stations if s["id"] not in placed]
    catch_all["stops"].extend(unplaced)

    problems = list(duplicates)
    if unplaced:
        problems.append(
            f"{len(unplaced)} station(s) are not placed by the journey spine and fell into "
            f"'{catch_all['title']}': {', '.join(s['id'] for s in unplaced)}"
        )
    return acts, problems


def check(stations: list[dict[str, Any]], acts: list[dict[str, Any]]) -> list[str]:
    """Hard failures. Coverage is the one that must never be waived."""
    problems: list[str] = []
    shown = [s["id"] for act in acts for s in act["stops"]]

    missing = {s["id"] for s in stations} - set(shown)
    if missing:
        problems.append(
            f"{len(missing)} station(s) are generated but appear nowhere in the walkthrough: "
            f"{', '.join(sorted(missing))}"
        )
    if len(shown) != len(set(shown)):
        problems.append("a station appears more than once in the walkthrough")

    for act in acts:
        if not act.get("title"):
            problems.append(f"{act.get('id')} has no title")
        if not act.get("catch_all") and not act.get("narrative"):
            problems.append(f"{act.get('id')} has no narrative; a stop list is not a review")

    return problems


# ---------------------------------------------------------------------------

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:#1a1d21;--muted:#5b6470;--faint:#8b94a0;--line:#e3e7ec;--bg:#fbfcfd;--card:#fff;
  --open:#b4530a;--open-bg:#fdf3e8;--settled:#2f6b4f;--settled-bg:#eef6f1;
  --accent:#1f4e79;--accent-bg:#eef3f9;--warn:#8a2b2b;--warn-bg:#fbeeee;
}
body{font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
.wrap{display:flex;min-height:100vh;max-width:1400px;margin:0 auto}
nav{width:270px;flex:0 0 270px;padding:26px 18px;border-right:1px solid var(--line);
  position:sticky;top:0;height:100vh;overflow-y:auto;background:var(--card)}
nav h1{font-size:15px;line-height:1.35;margin-bottom:4px}
nav .sub{font-size:12px;color:var(--faint);margin-bottom:18px}
nav a{display:block;padding:8px 10px;border-radius:6px;text-decoration:none;color:var(--muted);
  font-size:13.5px;line-height:1.35;margin-bottom:2px;border-left:3px solid transparent}
nav a:hover{background:var(--bg);color:var(--ink)}
nav a.done{color:var(--settled);border-left-color:var(--settled)}
nav a .n{font-variant-numeric:tabular-nums;font-size:11px;color:var(--faint);float:right}
main{flex:1;padding:40px 48px 120px;max-width:920px}
.act{margin-bottom:64px;scroll-margin-top:20px}
.eyebrow{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--faint);
  font-weight:600;margin-bottom:8px}
h2{font-size:29px;line-height:1.2;letter-spacing:-.015em;margin-bottom:10px}
.lede{font-size:18px;color:var(--muted);margin-bottom:18px;line-height:1.5}
.narrative{font-size:16.5px;margin-bottom:14px;white-space:pre-wrap}
.notlist{background:var(--warn-bg);border-left:3px solid var(--warn);padding:12px 16px;
  border-radius:0 6px 6px 0;margin:16px 0;font-size:14.5px}
.notlist b{display:block;margin-bottom:5px;font-size:12px;letter-spacing:.05em;
  text-transform:uppercase;color:var(--warn)}
.notlist div{color:var(--muted);margin:3px 0}
.stop{background:var(--card);border:1px solid var(--line);border-radius:9px;margin:12px 0;
  overflow:hidden;transition:border-color .15s}
.stop.answered{border-color:var(--settled)}
.head{padding:15px 18px;cursor:pointer;display:flex;gap:12px;align-items:flex-start}
.head:hover{background:var(--bg)}
.badge{flex:0 0 auto;font-size:10.5px;font-weight:700;letter-spacing:.05em;padding:3px 8px;
  border-radius:4px;text-transform:uppercase;margin-top:2px;white-space:nowrap}
.b-open{background:var(--open-bg);color:var(--open)}
.b-set{background:var(--settled-bg);color:var(--settled)}
.q{flex:1;font-size:15.5px;line-height:1.45}
.tick{flex:0 0 auto;font-size:12px;color:var(--settled);font-weight:600;margin-top:3px}
.body{display:none;padding:0 18px 18px;border-top:1px solid var(--line)}
.stop.open .body{display:block}
.field{margin-top:15px}
.field .k{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);
  font-weight:600;margin-bottom:4px}
.field .v{font-size:15px;color:var(--ink);white-space:pre-wrap}
.rec{background:var(--accent-bg);border-left:3px solid var(--accent);padding:13px 16px;
  border-radius:0 6px 6px 0;margin-top:15px}
.rec .k{color:var(--accent)}
.rec .disc{font-size:12.5px;color:var(--muted);margin-top:8px;font-style:italic}
.opts{margin-top:6px}
.opts li{margin:4px 0 4px 20px;font-size:15px}
.ev{font-size:13px;color:var(--muted);margin:3px 0 3px 20px}
.ctl{margin-top:18px;padding-top:16px;border-top:1px dashed var(--line)}
.btns{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:10px}
button.r{font:inherit;font-size:13.5px;padding:7px 15px;border:1px solid var(--line);
  background:var(--card);border-radius:6px;cursor:pointer;color:var(--muted)}
button.r:hover{border-color:var(--muted);color:var(--ink)}
button.r.sel{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
textarea{width:100%;font:inherit;font-size:14.5px;padding:10px 12px;border:1px solid var(--line);
  border-radius:6px;resize:vertical;min-height:74px;background:var(--card);color:var(--ink)}
.hint{font-size:12.5px;color:var(--faint);margin-top:5px}
.hint.req{color:var(--warn);font-weight:600}
.bar{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--line);
  padding:11px 24px;display:flex;gap:12px;align-items:center;justify-content:center;
  font-size:13.5px;z-index:20;flex-wrap:wrap}
.bar b{font-variant-numeric:tabular-nums}
button.p{font:inherit;font-size:13.5px;padding:8px 17px;border-radius:6px;cursor:pointer;
  border:1px solid var(--accent);background:var(--accent);color:#fff;font-weight:600}
button.s{font:inherit;font-size:13.5px;padding:8px 17px;border-radius:6px;cursor:pointer;
  border:1px solid var(--line);background:var(--card);color:var(--muted)}
.warnbar{background:var(--warn-bg);color:var(--warn);padding:9px 24px;text-align:center;
  font-size:13.5px;border-bottom:1px solid #f0dede}
@media(max-width:860px){.wrap{flex-direction:column}nav{width:100%;flex:none;position:static;
  height:auto;border-right:none;border-bottom:1px solid var(--line)}main{padding:26px 20px 130px}}
@media print{nav,.bar,.ctl,.warnbar{display:none}.body{display:block!important}}
"""

JS = """
const S={};   // station id -> {response, reason, choice}
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}

function count(){
  const done=Object.values(S).filter(v=>v&&v.response).length;
  document.getElementById('done').textContent=done;
  DATA.acts.forEach(a=>{
    const el=document.getElementById('nav-'+a.id); if(!el) return;
    const ids=a.stops.map(s=>s.id), d=ids.filter(i=>S[i]&&S[i].response).length;
    el.querySelector('.n').textContent=ids.length?d+'/'+ids.length:'';
    el.classList.toggle('done', ids.length>0 && d===ids.length);
  });
}

function pick(id,verdict,btn){
  S[id]=S[id]||{}; S[id].response=verdict;
  const card=document.getElementById('c-'+id);
  card.querySelectorAll('button.r').forEach(b=>b.classList.remove('sel'));
  btn.classList.add('sel');
  const need=DATA.reasonRequired.includes(verdict);
  const hint=card.querySelector('.reason-hint');
  hint.classList.toggle('req',need);
  hint.textContent=need
    ? 'A reason is required. It is kept as a standing constraint, so the design is not re-proposed to you unchanged.'
    : 'Add anything you want recorded (optional).';
  card.classList.toggle('answered', !!S[id].response);
  card.querySelector('.tick').textContent=S[id].response?S[id].response:'';
  count();
}
function note(id,el){S[id]=S[id]||{};S[id].reason=el.value}
function choose(id,el){S[id]=S[id]||{};S[id].choice=el.value}
function toggle(id){document.getElementById('c-'+id).classList.toggle('open')}

function missing(){
  return Object.entries(S).filter(([id,v])=>v.response&&DATA.reasonRequired.includes(v.response)
    && !(v.reason||'').trim()).map(([id])=>id);
}

function save(){
  const m=missing();
  if(m.length && !confirm(m.length+' response(s) need a reason and do not have one:\\n\\n'+m.join('\\n')
     +'\\n\\nA change without a reason cannot be compiled. Export anyway as a draft?')) return;
  const out={sitting:DATA.sitting,generated_from:DATA.commit,
    responses:Object.entries(S).filter(([i,v])=>v.response).map(([id,v])=>({
      station:id,response:v.response,chosen_option:v.choice||null,reason:v.reason||''}))};
  const b=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(b);
  a.download='ccc-walkthrough-responses.json';a.click();
}

function load(ev){
  const f=ev.target.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{try{
    const d=JSON.parse(r.result);
    (d.responses||[]).forEach(x=>{S[x.station]={response:x.response,reason:x.reason||'',choice:x.chosen_option||''}});
    render(); alert('Restored '+(d.responses||[]).length+' response(s).');
  }catch(e){alert('That file could not be read: '+e.message)}};
  r.readAsText(f);
}

function stopHTML(s){
  const open=DATA.decisionKinds.includes(s.kind);
  const st=S[s.id]||{};
  let h='<div class="stop'+(st.response?' answered':'')+'" id="c-'+s.id+'">';
  h+='<div class="head" onclick="toggle(\\''+s.id+'\\')">';
  h+='<span class="badge '+(open?'b-open':'b-set')+'">'+(open?'open':'settled')+'</span>';
  h+='<span class="q">'+esc(s.prompt)+'</span>';
  h+='<span class="tick">'+esc(st.response||'')+'</span></div>';
  h+='<div class="body">';
  h+='<div class="field"><div class="k">What is built</div><div class="v">'+esc(s.what_we_built)+'</div></div>';
  if(s.why_held_open) h+='<div class="field"><div class="k">Why this is held open</div><div class="v">'+esc(s.why_held_open)+'</div></div>';
  if(s.options&&s.options.length){
    h+='<div class="field"><div class="k">The declared range</div><ul class="opts">';
    s.options.forEach(o=>h+='<li>'+esc(o)+'</li>');h+='</ul></div>';
  }
  const r=s.recommendation||{};
  if(r.present){
    h+='<div class="rec"><div class="k">Recommendation</div>';
    if(r.option)h+='<div class="v"><b>'+esc(r.option)+'</b></div>';
    if(r.rationale)h+='<div class="v" style="margin-top:6px">'+esc(r.rationale)+'</div>';
    (r.comparators||[]).forEach(c=>h+='<div class="ev">Comparator: '+esc(c)+'</div>');
    (r.evidence||[]).forEach(e=>h+='<div class="ev">Evidence: '+esc(e)+'</div>');
    if(r.confidence)h+='<div class="ev">Confidence: '+esc(r.confidence)+
      (r.confidence_basis?' &mdash; '+esc(r.confidence_basis):'')+'</div>';
    if(r.what_would_change_it)h+='<div class="ev"><b>What would change this:</b> '+esc(r.what_would_change_it)+'</div>';
    if(r.owner)h+='<div class="ev">Owner: '+esc(r.owner)+'</div>';
    h+='<div class="disc">A recommendation, not a decision. Only the committee decides.</div></div>';
  } else if(open){
    h+='<div class="rec"><div class="k">No recommendation yet</div><div class="v">'+
       'The comparative research to support a recommendation here is still outstanding. '+
       'This is shown as an open question rather than dressed up as a proposal.</div></div>';
  }
  if(s.what_it_gates)h+='<div class="field"><div class="k">What this affects</div><div class="v">'+esc(s.what_it_gates)+'</div></div>';
  if(s.what_it_does_not_gate)h+='<div class="field"><div class="k">What it does NOT affect</div><div class="v">'+esc(s.what_it_does_not_gate)+'</div></div>';
  if(s.decide_by)h+='<div class="field"><div class="k">When the choice gets expensive</div><div class="v">'+esc(s.decide_by)+
    '<div class="hint" style="margin-top:5px">'+esc(s.decide_by_meaning||'')+'</div></div></div>';
  if(s.risk)h+='<div class="field"><div class="k">Risk if it does not hold</div><div class="v">'+esc(s.risk)+'</div></div>';
  if(s.tested_by)h+='<div class="field"><div class="k">How it would be tested</div><div class="v">'+esc(s.tested_by)+'</div></div>';
  if(s.note)h+='<div class="field"><div class="k">Note</div><div class="v">'+esc(s.note)+'</div></div>';
  if(s.reopening_note)h+='<div class="field"><div class="k">Reopening</div><div class="v">'+esc(s.reopening_note)+'</div></div>';
  h+='<div class="field"><div class="k">Where this lives</div><div class="v" style="font-size:13px;color:var(--faint)">'+esc(s.source)+'</div></div>';

  h+='<div class="ctl"><div class="btns">';
  (s.response.allowed||[]).forEach(v=>{
    h+='<button class="r'+(st.response===v?' sel':'')+'" onclick="pick(\\''+s.id+'\\',\\''+v+'\\',this)">'+v+'</button>';
  });
  h+='</div>';
  if(s.options&&s.options.length){
    h+='<div class="field" style="margin-top:0"><div class="k">Which option</div>'+
       '<textarea style="min-height:38px" placeholder="Type or paste the option you want, or your own wording" '+
       'oninput="choose(\\''+s.id+'\\',this)">'+esc(st.choice||'')+'</textarea></div>';
  }
  h+='<textarea style="margin-top:8px" placeholder="Your reason, question or amendment" '+
     'oninput="note(\\''+s.id+'\\',this)">'+esc(st.reason||'')+'</textarea>';
  const need=st.response&&DATA.reasonRequired.includes(st.response);
  h+='<div class="hint reason-hint'+(need?' req':'')+'">'+(need
    ?'A reason is required. It is kept as a standing constraint, so the design is not re-proposed to you unchanged.'
    :'Add anything you want recorded (optional).')+'</div>';
  h+='</div></div></div>';
  return h;
}

function render(){
  let nav='',body='';
  // The catch-all act renders only when it has caught something, so the act count
  // must be the VISIBLE count -- "Act 4 of 10" beside nine acts reads as a missing page.
  const acts=DATA.acts.filter(a=>!(a.catch_all && !a.stops.length));
  acts.forEach((a,i)=>{
    nav+='<a href="#'+a.id+'" id="nav-'+a.id+'">'+esc(a.title)+'<span class="n"></span></a>';
    body+='<section class="act" id="'+a.id+'">';
    body+='<div class="eyebrow">Act '+(i+1)+' of '+acts.length+'</div>';
    body+='<h2>'+esc(a.title)+'</h2>';
    if(a.lede)body+='<p class="lede">'+esc(a.lede)+'</p>';
    if(a.narrative)body+='<p class="narrative">'+esc(a.narrative)+'</p>';
    if(a.what_it_is_not){
      body+='<div class="notlist"><b>What it is not</b>';
      a.what_it_is_not.forEach(x=>body+='<div>'+esc(x)+'</div>');
      body+='</div>';
    }
    a.stops.forEach(s=>body+=stopHTML(s));
    body+='</section>';
  });
  document.getElementById('nav').innerHTML=nav;
  document.getElementById('acts').innerHTML=body;
  count();
}
render();
"""



# ---------------------------------------------------------------------------
# The reviewer's language
# ---------------------------------------------------------------------------

LANGUAGE_PATH = ROOT / "engine/schemas/reviewer-language.yaml"

_URL_RE = re.compile(r"https?://\S+")


def load_language() -> dict[str, Any]:
    if not LANGUAGE_PATH.is_file():
        raise WalkthroughError(f"{LANGUAGE_PATH.relative_to(ROOT)} does not exist.")
    return yaml.safe_load(LANGUAGE_PATH.read_text(encoding="utf-8"))


_REPO_PATH_RE = re.compile(r"\b(?:canon|engine|workstreams|governance|documents)/[\w./-]+")

# "Marketing copy (W14)" -> "Marketing copy". The human label already carries the
# meaning; translating the parenthetical only duplicates it.
_PARENTHETICAL_ID_RE = re.compile(r"\s*\((?:(?:[FQW]\d{2,3}(?:-\d{2})?)|UA\d+)\)")

# Facts, questions, workstreams and dossiers all share a shape; assumptions do
# not. UA3 slipped through the first version of this pattern and was caught only
# by the leak check — which is the argument for having the leak check.
_ID_RE = re.compile(r"\b((?:[FQW]\d{2,3}(?:-\d{2})?)|UA\d+)\b")

# Words that carry no content when deciding whether the text after an identifier
# already says what the identifier's name would say.
_STOPWORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "is", "it", "its",
    "of", "on", "or", "that", "the", "this", "to", "under", "was", "with", "will",
}


def translate(text: str, lang: dict[str, Any]) -> str:
    """Replace internal identifiers with plain-language names.

    Order matters, and each step exists because the obvious version produced
    something worse than the identifier it replaced.

    URLs are masked first: a path inside a link the reviewer can follow is not an
    instruction to open a file they cannot. Repository paths go next, WHOLE,
    before any identifier inside them is translated — otherwise
    "workstreams/W16/working/x.md" becomes the nonsense
    "workstreams/commercial and pricing/working/x.md".

    Compound forms next, because "W07-01 condition 6" translated in two pieces
    yields "the admissions decision condition 6".

    Then parentheticals, because "Marketing copy (W14)" translated in place gives
    "Marketing copy (marketing)".

    Finally the bare identifiers, and this is the subtle one. Where an identifier
    is immediately followed by the words that describe it — "F026 indemnity
    trigger" — translating gives "the indemnity trigger indemnity trigger", so the
    identifier is dropped and the words kept. But that test has to be about
    MEANING, not word shape: a first attempt dropped any identifier followed by a
    lowercase word, which turned "Established by W03 on 2026-08-02" into
    "Established by on 2026-08-02". So the following words are compared against
    the identifier's own name, ignoring stopwords, and the identifier is dropped
    only when they genuinely say the same thing.
    """
    masked: list[str] = []

    def _mask(match: re.Match) -> str:
        masked.append(match.group(0))
        return f"\x00{len(masked) - 1}\x00"

    text = _URL_RE.sub(_mask, text)
    text = _REPO_PATH_RE.sub(lang.get("path_replacement", "the research record"), text)

    for pattern, replacement in (lang.get("compound_translations") or {}).items():
        text = re.sub(pattern, replacement, text)

    # Longest phrase first, so "approved canon" is not eaten by "canon".
    phrases = lang.get("phrase_translations") or {}
    for phrase in sorted(phrases, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(phrase)}\b", phrases[phrase], text, flags=re.IGNORECASE)

    if lang.get("drop_parenthetical_identifiers"):
        text = _PARENTHETICAL_ID_RE.sub("", text)

    names = lang.get("translations") or {}

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        name = names.get(key)
        if not name:
            return key                      # unknown identifier: leave it to the leak check
        tail = text[match.end():match.end() + 70]
        following = re.match(r"\s+([A-Za-z][\w'-]*(?:\s+[A-Za-z][\w'-]*){0,2})", tail)
        if following and lang.get("drop_identifier_prefixes"):
            words = [w.lower() for w in following.group(1).split()
                     if w.lower() not in _STOPWORDS]
            if words and all(w in name.lower() for w in words):
                return ""                   # the words after it already say this
        return name

    text = _ID_RE.sub(_replace, text)

    # Dropping an identifier leaves the space that preceded it.
    text = re.sub(r"[ \t]{2,}", " ", text).replace(" ,", ",").replace(" .", ".")

    for index, original in enumerate(masked):
        text = text.replace(f"\x00{index}\x00", original)
    return text


def reviewer_view(node: Any, lang: dict[str, Any], key: str | None = None) -> Any:
    """Strip plumbing, translate prose, keep only citations a reviewer can open.

    A committee member has no access to this repository, so an untranslated
    identifier does not merely read as jargon — it points at something they
    cannot open, and signals the document was written for somebody else.
    """
    omit = set(lang.get("omit_fields") or [])

    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k in omit:
                continue
            # Station ids go; act ids stay, because they are the page's anchors.
            if k == "id" and isinstance(v, str) and v.startswith("ST-"):
                continue
            if k == "evidence" and lang.get("evidence_must_be_reachable"):
                # A repository path is provenance for the programme office and a
                # dead end for a reviewer. Keep only what they can actually follow
                # — but never go silent: a recommendation showing no evidence line
                # reads as unevidenced when it is not.
                reachable = [e for e in v if isinstance(e, str) and "http" in e]
                if len(reachable) < len(v) and lang.get("evidence_unreachable_note"):
                    reachable.append(lang["evidence_unreachable_note"])
                v = reachable
                if not v:
                    continue
            out[k] = reviewer_view(v, lang, k)
        return out
    if isinstance(node, list):
        return [reviewer_view(v, lang, key) for v in node]
    if isinstance(node, str):
        return translate(node, lang)
    return node


def check_no_internal_leaks(rendered: str, lang: dict[str, Any]) -> list[str]:
    """Fail the build if an internal reference survived into the page.

    URLs are excluded before checking: a live citation is a link the reviewer can
    follow, and a path inside it is not an instruction to open a file they cannot
    see. This mirrors the controlled-vocabulary check, which learned the same
    lesson — a rule that cannot distinguish a citation from an instruction ends up
    either too loud to obey or quietly switched off.
    """
    stripped = _URL_RE.sub(" ", rendered)
    problems = []
    for rule in lang.get("leak_patterns") or []:
        found = sorted(set(re.findall(rule["pattern"], stripped)))
        found = [f for f in found if f]
        if found:
            problems.append(
                f"{rule['name']} leaked into reviewer-facing text: "
                f"{', '.join(found[:8])}{' ...' if len(found) > 8 else ''}"
            )
    return problems


def build_html(acts: list[dict[str, Any]], stations: list[dict[str, Any]], commit: str) -> str:
    lang = load_language()
    # Drop an empty catch-all BEFORE redaction, while the flag still exists. The
    # JS used to do this, but `catch_all` is redacted away, so the page rendered a
    # blank final act — a regression the stop-count test could not see because the
    # act had no stops to count.
    acts = [a for a in acts if not (a.get("catch_all") and not a.get("stops"))]
    # Everything below this line is what a committee member will actually read.
    acts = reviewer_view(acts, lang)
    data = {
        "acts": acts,
        "sitting": "CCC design walkthrough",
        "commit": commit,
        "reasonRequired": sorted(di.REASON_REQUIRED),
        "decisionKinds": sorted(di.DECISION_KINDS),
    }
    payload = json.dumps(data, default=str)
    leaks = check_no_internal_leaks(payload, lang)
    if leaks:
        raise WalkthroughError(
            "the page carries internal references a reviewer cannot resolve:\n  - "
            + "\n  - ".join(leaks)
        )
    total = len(stations)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>QIPS Professional Programme — CCC design walkthrough</title>
<style>{CSS}</style></head><body>
<div class="warnbar">Draft for CCC review. Nothing here is decided, published, or final.
Your progress is held in this page only — use <b>Save my responses</b> before closing the tab.</div>
<div class="wrap">
<nav>
  <h1>QIPS Professional Programme</h1>
  <div class="sub">Cohort 1 &middot; SQHN and Partners<br>Design walkthrough for the CCC</div>
  <div id="nav"></div>
</nav>
<main><div id="acts"></div></main>
</div>
<div class="bar">
  <span><b id="done">0</b> of <b>{total}</b> answered</span>
  <button class="p" onclick="save()">Save my responses</button>
  <label class="s" style="cursor:pointer">Resume from a saved file
    <input type="file" accept="application/json" onchange="load(event)" style="display:none"></label>
</div>
<script>const DATA={payload};</script>
<script>{JS}</script>
</body></html>
"""


# ---------------------------------------------------------------------------

def self_test() -> int:
    failures: list[str] = []
    stations = di.build_stations()
    journey = load_journey()
    acts, anchor_problems = anchor(stations, journey)

    for problem in check(stations, acts):
        failures.append(f"check: {problem}")

    # coverage: every generated station must be reachable in the page
    shown = {s["id"] for act in acts for s in act["stops"]}
    if shown != {s["id"] for s in stations}:
        failures.append("the walkthrough does not show every generated station")

    # a settled fact must be challengeable, an open one must not be merely noted
    review = [s for s in stations if s["kind"] == "REVIEW_POINT"]
    if not review:
        failures.append("no review points generated; settled facts could not be challenged")
    for station in review:
        if "CHALLENGE" not in station["response"]["allowed"]:
            failures.append(f"{station['id']}: settled fact cannot be challenged")
    for station in stations:
        if station["kind"] in di.DECISION_KINDS and "ACCEPT" not in station["response"]["allowed"]:
            failures.append(f"{station['id']}: open item offers no way to accept it")

    try:
        html_out = build_html(acts, stations, "self-test")
    except WalkthroughError as exc:
        # A leak is a legitimate hard failure, but it should read as a stated
        # defect rather than as a crash — the message is what the next person sees.
        print(f"  FAIL  page refused to build: {exc}", file=sys.stderr)
        return 1

    # the page must be genuinely self-contained and storage-free
    for forbidden in ("localStorage", "sessionStorage", "indexedDB"):
        if forbidden in html_out:
            failures.append(f"page uses {forbidden}; it must hold state in memory only")
    for external in ("<script src=", "<link rel=\"stylesheet\"", "@import"):
        if external in html_out:
            failures.append(f"page loads an external resource ({external}); it must be self-contained")

    # Every station must still REACH the page — but not by its identifier, which
    # is now deliberately withheld. Counting the rendered stops proves presence
    # without reintroducing the leak this design exists to close.
    try:
        payload = json.loads(re.search(r"const DATA=(\{.*\});</script>", html_out, re.S).group(1))
        rendered = sum(len(act.get("stops", [])) for act in payload["acts"])
    except Exception as exc:
        failures.append(f"could not parse the page payload to count stops: {exc}")
    else:
        if rendered != len(stations):
            failures.append(
                f"{len(stations)} stations generated but {rendered} reached the page"
            )

    # the reason hint must be uniquely addressable — a decide_by hint used to
    # steal the "reason required" message because both carried the same class
    if "reason-hint" not in html_out:
        failures.append("the reason hint is not uniquely addressable; another hint can steal it")

    # --- reviewer language -------------------------------------------------
    lang = load_language()

    # the leak check must actually bite, on every pattern it claims to cover
    for probe, label in [
        ("this depends on F024", "fact identifier"),
        ("see Q001 for detail", "question identifier"),
        ("owned by W16", "workstream identifier"),
        ("rests on UA3", "assumption identifier"),
        ("generated by ST-F020", "station identifier"),
        ("see workstreams/W16/working/x.md", "repository path"),
        ("run engine/walkthrough.py", "engine filename"),
        ("under condition 6", "bare condition"),
    ]:
        if not check_no_internal_leaks(probe, lang):
            failures.append(f"leak check does not catch a {label}: {probe!r}")

    # a live citation must NOT be treated as a leak
    citation = "see https://example.test/workstreams/W16/thing.yaml for the source"
    if check_no_internal_leaks(citation, lang):
        failures.append("leak check flags a live citation; a link is not an instruction")

    # translation must not produce something worse than the identifier
    for before, must_not_contain in [
        ("Marketing copy (W14)", "("),
        ("F026 indemnity trigger", "trigger trigger"),
    ]:
        after = translate(before, lang)
        if must_not_contain in after:
            failures.append(f"translation of {before!r} produced {after!r}")
    # and must not swallow a workstream that is genuinely being named
    if "by  on" in translate("Established by W03 on 2026-08-02", lang):
        failures.append("translation dropped an identifier that was not duplicated")

    # the rendered page itself must be clean
    for problem in check_no_internal_leaks(html_out, lang):
        failures.append(f"rendered page: {problem}")

    # Navigation must actually resolve. Omitting `id` wholesale once stripped it
    # from acts as well as stations, leaving every nav link pointing at
    # "#undefined" — a page that looked correct and could not be navigated.
    view = reviewer_view(acts, lang)
    for act in view:
        if not act.get("id"):
            failures.append(f"an act lost its id; its navigation link cannot resolve")
        for stop in act.get("stops", []):
            if "id" in stop:
                failures.append("a station id survived into the reviewer's view")

    # No act may render empty. An empty act is either a spine defect or a
    # redaction defect, and both look identical to a reviewer: a heading with
    # nothing under it.
    try:
        shown = json.loads(re.search(r"const DATA=(\{.*\});</script>", html_out, re.S).group(1))
        for act in shown["acts"]:
            if not act.get("stops") and not act.get("narrative"):
                failures.append(f"act {act.get('id')} renders with nothing in it")
    except Exception:
        pass  # the payload-parse failure is already reported above

    # Insider vocabulary is a SECOND kind of leak, invisible to the identifier
    # check: "Canon is the only thing that is true" contains no identifier and is
    # still unreadable to anyone outside this repository. It was found by looking
    # at a screenshot, which is the argument for looking at screenshots.
    #
    # Note what this check does and does not do, because it looks weaker than it
    # is. It runs on the TRANSLATED text, so a term that has an entry in
    # phrase_translations never reaches it — the translation is the fix, and
    # writing "canon" in a narrative is therefore harmless. What this catches is
    # jargon with NO translation, which would otherwise reach the reviewer intact.
    # The two mechanisms divide cleanly: translate what has a plain equivalent,
    # refuse to ship what does not.
    JARGON = ["canon", "validator", "property test", "invariant", "promoted fact",
              "dossier", "proposal branch", "pull request", "repository",
              "self-test", "hardcoded", "payload", "schema"]
    body = json.dumps(reviewer_view(acts, lang), default=str).lower()
    for term in JARGON:
        if re.search(rf"\b{re.escape(term)}\b", body):
            failures.append(
                f"insider vocabulary reaching the reviewer: {term!r} — a committee member "
                "has no way to resolve it"
            )

    # the page must never claim to be a decision
    low = html_out.lower()
    for phrase in ("nothing here is decided", "not a decision"):
        if phrase not in low:
            failures.append(f"page does not carry the disclaimer {phrase!r}")

    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}", file=sys.stderr)
        return 1

    note = f" ({len(anchor_problems)} anchoring note(s))" if anchor_problems else ""
    print(f"walkthrough self-test: all checks passed — {len(stations)} stops, {len(acts)} acts{note}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out")
    parser.add_argument("--commit", default="working copy")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    stations = di.build_stations()
    journey = load_journey()
    acts, anchor_problems = anchor(stations, journey)
    problems = check(stations, acts)

    if args.check or not args.out:
        print(f"stops: {len(stations)}   acts: {len(acts)}")
        for act in acts:
            marker = "  <-- should be empty" if act.get("catch_all") and act["stops"] else ""
            print(f"  {act['id']:<6} {act['title']:<45} {len(act['stops']):>2}{marker}")
        if anchor_problems:
            print("\nanchoring notes:")
            for problem in anchor_problems:
                print(f"  {problem}")
        if problems:
            print()
            for problem in problems:
                print(f"  FAIL  {problem}", file=sys.stderr)
            return 1
        if not args.out:
            return 0

    if problems:
        for problem in problems:
            print(f"  FAIL  {problem}", file=sys.stderr)
        return 1

    Path(args.out).write_text(build_html(acts, stations, args.commit), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
