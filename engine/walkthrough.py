#!/usr/bin/env python3
"""Render the CCC design walkthrough as one self-contained HTML file.

WHY A SINGLE FILE
-----------------
The reviewer opens it in a browser. No login, no install, no server, works on a
phone, works offline, survives a dropped connection mid-session. It commits the
programme to no platform — the hosting question stays open, which matters while
Base44 may or may not be the final destination.

WHY IT IS A GUIDED WALK AND NOT A DOCUMENT
------------------------------------------
The first version was one long page with a contents list down the side. It was
readable, and it silently required somebody to sit beside the reviewer and
explain the shape of it: what she was looking at, why some items had
recommendations and others did not, how far in she was, what happened to
anything she wrote. A design surface that needs a narrator is a design surface
only one person can use.

So the page introduces itself, then takes one stop at a time, in an order the
spine controls, with each part introduced before its questions arrive. The whole
document is still there — one button away, for anyone who would rather read it
straight through — but nothing depends on finding it.

ON BROWSER STORAGE
------------------
This file DOES use localStorage, and the earlier version deliberately did not.
That was the right call while the page was a document to read and the only cost
of closing the tab was losing a few ticks. It became the wrong call the moment
the page asked for an hour of somebody's thinking: losing that costs far more
than the tidiness of a storage-free page. Autosave is primary; the file export
remains, because storage is per-browser and per-device and she may want to send
her answers to someone.

WHAT IT IS NOT
--------------
Not a mockup. Every stop is generated from engine/decision_interview.py, which is
generated from the repository. The narrative spine is data in
engine/schemas/walkthrough-journey.yaml. Nothing here is authored twice, so
nothing here can drift from the build.

Usage:
    python3 engine/walkthrough.py --out walkthrough.html   one file, works offline
    python3 engine/walkthrough.py --pwa site/              hosted form, installable
    python3 engine/walkthrough.py --check
    python3 engine/walkthrough.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
import urllib.parse
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
  --ink:#16191d;--muted:#5b6470;--faint:#8b94a0;--line:#e5e9ee;--bg:#f7f9fb;--card:#fff;
  --accent:#1f4e79;--accent-soft:#eef3f9;--warn:#8a2b2b;--warn-soft:#fbeeee;
  --ok:#2f6b4f;--ok-soft:#eef6f1;--open:#b4530a;--open-soft:#fdf3e8;
  --know:#5b3d86;--know-soft:#f3ecfa;--make:#8a2b2b;--make-soft:#fdf0f0;
  --shadow:0 1px 2px rgba(16,24,40,.04),0 4px 16px rgba(16,24,40,.06);
}
html{-webkit-text-size-adjust:100%}
body{font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
button,textarea,input{font:inherit;color:inherit}
button{cursor:pointer}

.top{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.92);
  backdrop-filter:saturate(1.6) blur(8px);border-bottom:1px solid var(--line)}
.top .inner{max-width:820px;margin:0 auto;padding:11px 24px;display:flex;gap:16px;align-items:center}
.brand{font-size:13.5px;font-weight:650;letter-spacing:-.01em;white-space:nowrap}
.brand span{display:block;font-size:11.5px;font-weight:400;color:var(--faint)}
.bar{flex:1;height:5px;background:var(--line);border-radius:3px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--accent);width:0;transition:width .35s ease}
.count{font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.saved{font-size:12px;color:var(--ok);opacity:0;transition:opacity .3s}
.saved.on{opacity:1}

main{max-width:820px;margin:0 auto;padding:38px 24px 150px}

h1{font-size:34px;line-height:1.15;letter-spacing:-.022em;margin-bottom:14px}
h2{font-size:27px;line-height:1.2;letter-spacing:-.018em;margin-bottom:10px}
h3{font-size:17px;margin-bottom:8px}
p{margin-bottom:14px}
.lede{font-size:19px;line-height:1.5;color:var(--muted);margin-bottom:20px}
.eyebrow{font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);
  font-weight:650;margin-bottom:10px}
.prose{font-size:16.5px;white-space:pre-wrap}
.quiet{color:var(--muted);font-size:14.5px}

.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:26px 28px;
  box-shadow:var(--shadow);margin-bottom:18px}
.panel{background:var(--bg);border:1px solid var(--line);border-radius:11px;padding:14px 16px;margin:14px 0}
.field{margin-top:16px}
.field .k{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--faint);
  font-weight:650;margin-bottom:5px}
.field .v{font-size:15.5px;white-space:pre-wrap}
.rec{background:var(--accent-soft);border-left:3px solid var(--accent);padding:15px 18px;
  border-radius:0 8px 8px 0;margin-top:16px}
.rec .k{color:var(--accent)}
.rec .disc{font-size:12.5px;color:var(--muted);margin-top:9px;font-style:italic}
.ev{font-size:13px;color:var(--muted);margin:4px 0 4px 18px}
.opts li{margin:5px 0 5px 20px;font-size:15.5px}
.notlist{background:var(--warn-soft);border-left:3px solid var(--warn);padding:13px 17px;
  border-radius:0 8px 8px 0;margin:16px 0;font-size:14.5px}
.notlist b{display:block;margin-bottom:6px;font-size:11.5px;letter-spacing:.06em;
  text-transform:uppercase;color:var(--warn)}
.notlist div{color:var(--muted);margin:4px 0}

.needs{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.05em;padding:4px 10px;
  border-radius:5px;text-transform:uppercase;white-space:nowrap}
.stophead{display:flex;gap:14px;align-items:flex-start;margin-bottom:6px}
.stophead h2,.stophead h3{flex:1;min-width:0}
.stophead h2.long{font-size:21px;line-height:1.32;letter-spacing:-.012em}
.stophead .needs{margin-top:7px}
.standing{background:var(--bg);border:1px solid var(--line);border-radius:10px;
  padding:12px 15px;margin:14px 0;font-size:14.5px;color:var(--muted)}
.standing .needs{margin-bottom:7px}
.n-YOUR_KNOWLEDGE{background:var(--know-soft);color:var(--know)}
.n-YOUR_JUDGEMENT{background:var(--open-soft);color:var(--open)}
.n-ARGUE_WITH_US{background:var(--accent-soft);color:var(--accent)}
.n-DESIGN_WITH_US{background:var(--make-soft);color:var(--make)}
.n-CHALLENGE_IF_WRONG{background:var(--ok-soft);color:var(--ok)}
.invite{font-size:15px;color:var(--muted);margin:12px 0 4px;padding-left:14px;
  border-left:2px solid var(--line);font-style:italic}

.btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 12px}
button.r{font-size:14px;padding:9px 17px;border:1px solid var(--line);background:var(--card);
  border-radius:8px;color:var(--muted);transition:all .12s}
button.r:hover{border-color:var(--muted);color:var(--ink)}
button.r.sel{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
button.p{font-size:14.5px;padding:11px 22px;border-radius:9px;border:1px solid var(--accent);
  background:var(--accent);color:#fff;font-weight:600}
button.p:disabled{opacity:.4;cursor:not-allowed}
button.s{font-size:14.5px;padding:11px 20px;border-radius:9px;border:1px solid var(--line);
  background:var(--card);color:var(--muted)}
button.s:disabled{opacity:.4;cursor:not-allowed}
.ta{position:relative}
textarea{width:100%;font-size:15.5px;padding:12px 46px 12px 14px;border:1px solid var(--line);
  border-radius:9px;resize:vertical;min-height:88px;background:var(--card)}
textarea:focus{outline:2px solid var(--accent-soft);border-color:var(--accent)}
.mic{position:absolute;top:9px;right:9px;width:30px;height:30px;border-radius:8px;
  border:1px solid var(--line);background:var(--card);display:flex;align-items:center;
  justify-content:center;font-size:12px;line-height:1;color:var(--muted)}
.mic.live{background:var(--warn);border-color:var(--warn);color:#fff;animation:pulse 1.3s infinite}
.mic[disabled]{opacity:.3;cursor:not-allowed}
.mic svg{pointer-events:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}
.hint{font-size:13px;color:var(--faint);margin-top:6px}
.hint.req{color:var(--warn);font-weight:600}

.nav{position:fixed;bottom:0;left:0;right:0;background:rgba(255,255,255,.94);
  backdrop-filter:saturate(1.6) blur(8px);border-top:1px solid var(--line);z-index:30}
.nav .inner{max-width:820px;margin:0 auto;padding:13px 24px;display:flex;gap:10px;align-items:center}
.nav .spacer{flex:1}

.legend div{font-size:14px;color:var(--muted);margin:9px 0;display:flex;gap:12px;align-items:baseline}
.raised-item{background:var(--make-soft);border-left:3px solid var(--make);padding:11px 15px;
  border-radius:0 7px 7px 0;margin:9px 0;font-size:14.5px}
.raised-item b{color:var(--make)}
.doc .stopwrap{border-top:1px solid var(--line);padding-top:22px;margin-top:22px}
.warnbar{background:var(--open-soft);color:var(--open);padding:9px 24px;text-align:center;
  font-size:13px}
/* Mobile is not a smaller desktop. Two things broke there and both were only
   visible in a narrow viewport: the needs badge sat beside the heading and ran
   off the right edge, and the navigation wrapped so that Back and Next landed on
   different rows. */
@media(max-width:640px){
  main{padding:24px 15px 128px} h1{font-size:26px} h2{font-size:21px}
  .card{padding:19px 17px;border-radius:12px} .top .inner{padding:9px 14px;gap:11px}
  .brand span{display:none} .count{font-size:11.5px}
  .needs{white-space:normal}
  .stophead{flex-direction:column-reverse;gap:9px}
  .stophead .needs{margin-top:0;align-self:flex-start}
  #resumed{display:none}
  .nav .inner{padding:10px 14px;display:grid;grid-template-columns:1fr 1fr;gap:8px}
  .nav .spacer{display:none}
  #back{grid-area:1/1} #fwd{grid-area:1/2}
  .nav [data-act="export"]{grid-area:2/1} .nav label.s{grid-area:2/2}
  .nav button,.nav label.s{padding:11px 8px;justify-content:center;text-align:center;font-size:14px}
}
@media print{.top,.nav,.mic,.warnbar{display:none}.card{box-shadow:none;page-break-inside:avoid}}
"""

JS = """
const KEY='qips-ccc-walkthrough-v1';
let S={answers:{},raised:[],act:0,stop:-1,mode:'welcome',_draft:{}};

function esc(s){const d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}
function acts(){return DATA.acts.filter(a=>a.stops&&a.stops.length)}
function allStops(){return acts().flatMap(a=>a.stops)}
function answered(){return Object.values(S.answers).filter(v=>v&&v.response).length}

/* Persistence. An earlier version deliberately held everything in memory and made
   the reviewer download a file. That was the wrong call once pausing and coming
   back became a requirement: losing an hour of someone's thinking costs far more
   than the tidiness of avoiding browser storage. Autosave is primary now; the
   file export stays, because storage is per-browser and she may want to send it. */
function persist(){
  try{
    localStorage.setItem(KEY,JSON.stringify({answers:S.answers,raised:S.raised,
      act:S.act,stop:S.stop,mode:S.mode,at:new Date().toISOString()}));
    const el=document.getElementById('saved');
    if(el){el.classList.add('on');clearTimeout(window._st);
      window._st=setTimeout(function(){el.classList.remove('on')},1400);}
  }catch(e){}
}
function restore(){
  try{const raw=localStorage.getItem(KEY);return raw?JSON.parse(raw):null}catch(e){return null}
}

/* Dictation. Speech recognition is a browser feature, not something this page can
   ship, so every failure path has to leave her able to type: no support, refused
   permission, no network. Each says which it is — "it did not work" would send
   her looking for a fault in the page. */
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
const MIC='<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" '+
  'stroke-width="2" stroke-linecap="round"><rect x="9" y="2" width="6" height="11" rx="3"/>'+
  '<path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>';
const STOPICON='<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor">'+
  '<rect x="5" y="5" width="14" height="14" rx="2.5"/></svg>';
let rec=null,recTarget=null;
function micIdle(btn){btn.classList.remove('live');btn.innerHTML=MIC;
  btn.title=SR?'Speak instead of typing':'Dictation needs Chrome, Edge or Safari'}
function dictate(btn){
  const box=btn.parentElement.querySelector('textarea');
  if(!SR){alert('This browser cannot take dictation. Chrome, Edge and Safari can. '+
    'You can still type, and nothing else on the page depends on it.');return}
  if(rec){rec.stop();if(recTarget===box)return}
  rec=new SR();rec.continuous=true;rec.interimResults=true;rec.lang='en-GB';
  recTarget=box;let base=box.value?box.value.trim()+' ':'';
  btn.classList.add('live');btn.innerHTML=STOPICON;btn.title='Stop dictating';
  rec.onresult=function(e){
    let out='';
    for(let i=e.resultIndex;i<e.results.length;i++){out+=e.results[i][0].transcript}
    box.value=base+out;box.dispatchEvent(new Event('input',{bubbles:true}));
  };
  rec.onerror=function(e){
    micIdle(btn);
    if(e.error==='not-allowed')alert('The browser refused access to the microphone. '+
      'You can still type.');
    else if(e.error==='network')alert('Dictation needs an internet connection — the '+
      'browser sends the audio away to transcribe it. Everything else here works offline, '+
      'and you can still type.');
    rec=null;
  };
  rec.onend=function(){micIdle(btn);rec=null};
  try{rec.start()}catch(err){micIdle(btn);rec=null}
}
function box(cls,ph,val,min){
  return '<div class="ta"><textarea class="'+cls+'" placeholder="'+esc(ph)+'"'+
    (min?' style="min-height:'+min+'"':'')+'>'+esc(val||'')+'</textarea>'+
    '<button class="mic" data-mic="1"'+
    (SR?' title="Speak instead of typing"':' disabled title="Dictation needs Chrome, Edge or Safari"')+
    '>'+MIC+'</button></div>';
}

/* Statements that are true of a whole kind of stop rather than of any one stop.
   Python lifts them out; they are shown on the opening page and once at the top
   of each part that contains such stops. */
function standing(code){
  const b=(DATA.boilerplate||{})[code];if(!b)return '';
  let h='';
  Object.keys(b).forEach(function(f){
    h+='<div style="margin-top:6px"><b>'+esc(DATA.fieldLabels[f]||f)+'.</b> '+esc(b[f])+'</div>'});
  return h;
}

function screenWelcome(){
  const n=allStops().length,k={};
  allStops().forEach(function(s){if(s.needs)k[s.needs.code]=(k[s.needs.code]||0)+1});
  let h='<div class="card"><div class="eyebrow">'+esc(DATA.sitting)+'</div>';
  h+='<h1>'+esc(DATA.title)+'</h1>';
  h+='<p class="lede">'+esc(DATA.welcome.lede)+'</p>';
  DATA.welcome.paragraphs.forEach(function(t){h+='<p class="prose">'+esc(t)+'</p>'});
  h+='</div>';
  h+='<div class="card"><h3>What you will be asked for</h3>'+
     '<p class="quiet">Not one kind of thing. The questions differ in what they need from you, '+
     'and each says which it is.</p><div class="legend">';
  ['YOUR_KNOWLEDGE','YOUR_JUDGEMENT','ARGUE_WITH_US','DESIGN_WITH_US','CHALLENGE_IF_WRONG']
    .forEach(function(c){
      const ex=allStops().find(function(s){return s.needs&&s.needs.code===c});
      if(!ex)return;
      h+='<div><span class="needs n-'+c+'">'+esc(ex.needs.label)+'</span><span>'+
         esc(ex.needs.invitation)+' <b>('+(k[c]||0)+')</b>'+standing(c)+'</span></div>';
    });
  h+='</div></div>';
  h+='<div class="card"><h3>How this works</h3><ul class="opts">'+
     '<li>'+n+' stops across '+acts().length+' parts. Most people take it in more than one sitting.</li>'+
     '<li>Your answers save themselves. Close the tab and come back &mdash; it resumes where you stopped.</li>'+
     '<li>You can go back and change anything, at any point.</li>'+
     '<li>Prefer to talk? Every box has a microphone.</li>'+
     '<li>Nothing you do here changes the programme by itself. It becomes a proposal a person reviews.</li>'+
     '</ul></div>';
  return h;
}

function screenActIntro(a,i){
  const open=a.stops.filter(function(s){return s.needs&&s.needs.code!=='CHALLENGE_IF_WRONG'}).length;
  let h='<div class="card"><div class="eyebrow">Part '+(i+1)+' of '+acts().length+'</div>';
  h+='<h1>'+esc(a.title)+'</h1>';
  if(a.lede)h+='<p class="lede">'+esc(a.lede)+'</p>';
  if(a.narrative)h+='<p class="prose">'+esc(a.narrative)+'</p>';
  if(a.what_it_is_not){h+='<div class="notlist"><b>What it is not</b>';
    a.what_it_is_not.forEach(function(x){h+='<div>'+esc(x)+'</div>'});h+='</div>'}
  h+='<p class="quiet" style="margin-top:18px">'+a.stops.length+' stop'+(a.stops.length===1?'':'s')+
     ' ahead &mdash; '+open+' where something is open, '+(a.stops.length-open)+' already settled.</p>';
  h+='</div>';
  const codes=[];
  a.stops.forEach(function(s){if(s.needs&&codes.indexOf(s.needs.code)<0)codes.push(s.needs.code)});
  codes.forEach(function(c){
    const st=standing(c);if(!st)return;
    h+='<div class="standing"><span class="needs n-'+c+'">'+
       esc((a.stops.find(function(s){return s.needs.code===c})).needs.label)+'</span>'+
       '<div>True of every stop of this kind in this part, so it is said here rather than '+
       'on each of them.</div>'+st+'</div>';
  });
  return h;
}

function stopBody(s){
  let h='';
  if(s.needs&&s.needs.invitation)h+='<div class="invite">'+esc(s.needs.invitation)+
    (s.needs.why_this_classification?' '+esc(s.needs.why_this_classification):'')+'</div>';
  h+='<div class="field"><div class="k">What is built</div><div class="v">'+esc(s.what_we_built)+'</div></div>';
  if(s.why_held_open)h+='<div class="field"><div class="k">Why this is open</div><div class="v">'+esc(s.why_held_open)+'</div></div>';
  if(s.options&&s.options.length){h+='<div class="field"><div class="k">The range</div><ul class="opts">';
    s.options.forEach(function(o){h+='<li>'+esc(o)+'</li>'});h+='</ul></div>'}
  const r=s.recommendation||{};
  if(r.present){
    h+='<div class="rec"><div class="k">Our recommendation</div>';
    if(r.option)h+='<div class="v"><b>'+esc(r.option)+'</b></div>';
    if(r.rationale)h+='<div class="v" style="margin-top:8px">'+esc(r.rationale)+'</div>';
    (r.comparators||[]).forEach(function(c){h+='<div class="ev">Comparator: '+esc(c)+'</div>'});
    (r.evidence||[]).forEach(function(e){h+='<div class="ev">Evidence: '+esc(e)+'</div>'});
    if(r.confidence)h+='<div class="ev">Confidence: '+esc(r.confidence)+
      (r.confidence_basis?' &mdash; '+esc(r.confidence_basis):'')+'</div>';
    if(r.what_would_change_it)h+='<div class="ev"><b>What would change this:</b> '+esc(r.what_would_change_it)+'</div>';
    h+='<div class="disc">A recommendation, not a decision. Only the committee decides.</div></div>';
  }
  if(s.what_it_gates)h+='<div class="field"><div class="k">What this affects</div><div class="v">'+esc(s.what_it_gates)+'</div></div>';
  if(s.what_it_does_not_gate)h+='<div class="field"><div class="k">What it does not affect</div><div class="v">'+esc(s.what_it_does_not_gate)+'</div></div>';
  if(s.decide_by)h+='<div class="field"><div class="k">When the choice gets expensive</div><div class="v">'+esc(s.decide_by)+
    '<div class="hint" style="margin-top:6px">'+esc(s.decide_by_meaning||'')+'</div></div></div>';
  if(s.risk)h+='<div class="field"><div class="k">Risk if it does not hold</div><div class="v">'+esc(s.risk)+'</div></div>';
  if(s.tested_by)h+='<div class="field"><div class="k">How it would be tested</div><div class="v">'+esc(s.tested_by)+'</div></div>';
  if(s.note)h+='<div class="field"><div class="k">Note</div><div class="v">'+esc(s.note)+'</div></div>';
  if(s.reopening_note)h+='<div class="field"><div class="k">Reopening</div><div class="v">'+esc(s.reopening_note)+'</div></div>';
  return h;
}

function stopControls(s){
  const st=S.answers[s.key]||{};
  let h='<div class="field" style="margin-top:22px;border-top:1px dashed var(--line);padding-top:18px">';
  h+='<div class="k">Your response</div><div class="btns">';
  (s.response.allowed||[]).forEach(function(v){
    h+='<button class="r ans'+(st.response===v?' sel':'')+'" data-ans="'+v+'">'+v+'</button>'});
  h+='</div>';
  if(s.options&&s.options.length)h+=box('choice','Which option, or your own wording',st.choice,'40px');
  h+=box('reason','Your reason, question or amendment',st.reason);
  const need=st.response&&DATA.reasonRequired.indexOf(st.response)>=0;
  h+='<div class="hint reason-hint'+(need?' req':'')+'">'+(need
    ?'A reason is needed here. It is kept as a standing constraint, so this does not come back to you unchanged.'
    :'Optional, but anything you write is kept.')+'</div></div>';
  return h;
}

function screenStop(a,s,i,n){
  let h='<div class="card"><div class="eyebrow">'+esc(a.title)+' &middot; '+(i+1)+' of '+n+'</div>';
  h+='<div class="stophead"><h2'+(s.prompt.length>110?' class="long"':'')+'>'+esc(s.prompt)+'</h2>';
  if(s.needs)h+='<span class="needs n-'+s.needs.code+'">'+esc(s.needs.label)+'</span>';
  h+='</div>'+stopBody(s)+stopControls(s)+'</div>';
  return h;
}

function screenRaise(a){
  const mine=S.raised.filter(function(r){return r.act===a.id});
  const d=(S._draft||{})[a.id]||{};
  let h='<div class="card" data-raise="'+a.id+'"><div class="eyebrow">'+esc(a.title)+'</div>';
  h+='<h2>Anything we did not ask about?</h2>';
  h+='<p class="lede">Every question in this part came from something we already knew was open. '+
     'If a decision is missing, or one of these is framed wrongly, this is where to say so.</p>';
  h+='<p class="quiet">It goes into the record as work to open, not as an answer. Skip it if nothing comes to mind.</p>';
  h+='<div class="btns" style="margin-top:16px">';
  DATA.raiseKinds.forEach(function(k){
    h+='<button class="r rk'+(d.kind===k[0]?' sel':'')+'" data-kind="'+k[0]+'" title="'+esc(k[1])+'">'+
       esc(k[0].replace(/_/g,' ').toLowerCase())+'</button>'});
  h+='</div>';
  h+=box('rtitle','In a line: what is missing or wrong',d.title,'40px');
  h+=box('rdetail','Enough detail that someone who was not here can pick it up',d.detail);
  h+='<div style="margin-top:12px"><button class="r radd">Add to the record</button></div>';
  mine.forEach(function(r){
    h+='<div class="raised-item"><b>'+esc(r.kind.replace(/_/g,' ').toLowerCase())+'</b> &mdash; '+
       esc(r.title)+'<div class="quiet" style="margin-top:5px">'+esc(r.detail)+'</div></div>'});
  h+='</div>';
  return h;
}

function screenFinish(){
  const n=allStops().length,a=answered();
  let h='<div class="card"><h1>That is the whole design</h1>';
  h+='<p class="lede">You answered '+a+' of '+n+' stops and raised '+S.raised.length+
     ' thing'+(S.raised.length===1?'':'s')+' we had not asked about.</p>';
  h+='<p class="prose">Nothing here has changed the programme. Your answers become a proposal with '+
     'your reasons attached, which a person reviews before anything is adopted. Anything you '+
     'skipped stays open, and the design continues to work either way.</p>';
  if(a<n)h+='<p class="quiet">'+(n-a)+' stop'+(n-a===1?'':'s')+' unanswered. That is a legitimate '+
     'outcome rather than an omission, and you can go back to any of them.</p>';
  h+='<div class="btns" style="margin-top:20px">'+
     '<button class="p" data-act="export">Send my responses back</button>'+
     '<button class="s" data-act="doc">Read the whole thing as one document</button></div></div>';
  if(S.raised.length){
    h+='<div class="card"><h3>What you raised</h3>';
    S.raised.forEach(function(r){
      h+='<div class="raised-item"><b>'+esc(r.kind.replace(/_/g,' ').toLowerCase())+'</b> &mdash; '+
         esc(r.title)+'<div class="quiet" style="margin-top:5px">'+esc(r.detail)+'</div></div>'});
    h+='</div>';
  }
  return h;
}

function screenDoc(){
  let h='<div class="card"><h1>'+esc(DATA.title)+'</h1><p class="lede">'+esc(DATA.welcome.lede)+
        '</p><button class="s" data-act="guided">Back to the guided walk</button></div>';
  acts().forEach(function(a,i){
    h+='<div class="card doc"><div class="eyebrow">Part '+(i+1)+'</div><h2>'+esc(a.title)+'</h2>';
    if(a.lede)h+='<p class="lede">'+esc(a.lede)+'</p>';
    if(a.narrative)h+='<p class="prose">'+esc(a.narrative)+'</p>';
    if(a.what_it_is_not){h+='<div class="notlist"><b>What it is not</b>';
      a.what_it_is_not.forEach(function(x){h+='<div>'+esc(x)+'</div>'});h+='</div>'}
    a.stops.forEach(function(s){
      h+='<div class="stopwrap"><div class="stophead"><h3>'+esc(s.prompt)+'</h3>';
      if(s.needs)h+='<span class="needs n-'+s.needs.code+'">'+esc(s.needs.label)+'</span>';
      h+='</div>'+stopBody(s);
      const st=S.answers[s.key]||{};
      if(st.response)h+='<div class="panel"><b>You said:</b> '+esc(st.response)+
        (st.reason?' &mdash; '+esc(st.reason):'')+'</div>';
      h+='</div>';
    });
    h+='</div>';
  });
  h+='<div class="card"><h3>That is all of it</h3><p class="quiet">The guided walk asks '+
     'for a response at each stop and saves as you go.</p>'+
     '<button class="s" data-act="guided">Back to the guided walk</button></div>';
  return h;
}

function steps(){
  const out=[{t:'welcome'}];
  acts().forEach(function(a,ai){
    out.push({t:'actintro',a:ai});
    a.stops.forEach(function(s,si){out.push({t:'stop',a:ai,s:si})});
    out.push({t:'raise',a:ai});
  });
  out.push({t:'finish'});
  return out;
}
function stepIndex(){
  const all=steps();
  if(S.mode==='welcome')return 0;
  if(S.mode==='finish')return all.length-1;
  for(let i=0;i<all.length;i++){
    const x=all[i];
    if(S.stop===-2&&x.t==='raise'&&x.a===S.act)return i;
    if(S.stop===-1&&x.t==='actintro'&&x.a===S.act)return i;
    if(x.t==='stop'&&x.a===S.act&&x.s===S.stop)return i;
  }
  return 0;
}
function goto2(i){
  const all=steps();i=Math.max(0,Math.min(all.length-1,i));
  const x=all[i];
  S.mode=x.t==='welcome'?'welcome':(x.t==='finish'?'finish':'walk');
  if(x.t==='actintro'){S.act=x.a;S.stop=-1}
  if(x.t==='stop'){S.act=x.a;S.stop=x.s}
  if(x.t==='raise'){S.act=x.a;S.stop=-2}
  persist();render();window.scrollTo({top:0});
}

function exportFile(){
  const out={sitting:DATA.sitting,generated_from:DATA.commit,
    journey_fingerprint:DATA.journey_fingerprint,
    responses:Object.keys(S.answers).filter(function(k){return S.answers[k].response})
      .map(function(k){return {station:k,response:S.answers[k].response,
        chosen_option:S.answers[k].choice||null,reason:S.answers[k].reason||''}}),
    raised:S.raised};
  const b=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(b);
  a.download='qips-walkthrough-'+(new Date().toISOString().slice(0,10))+'.json';a.click();
}
function importFile(ev){
  const f=ev.target.files[0];if(!f)return;
  const r=new FileReader();
  r.onload=function(){try{
    const d=JSON.parse(r.result);
    (d.responses||[]).forEach(function(x){S.answers[x.station]={response:x.response,
      reason:x.reason||'',choice:x.chosen_option||''}});
    S.raised=d.raised||[];persist();render();
    alert('Restored '+(d.responses||[]).length+' response(s).');
  }catch(e){alert('That file could not be read: '+e.message)}};
  r.readAsText(f);
}

function render(){
  const all=steps(),i=stepIndex(),x=all[i];
  let body='';
  if(S.mode==='doc')body=screenDoc();
  else if(x.t==='welcome')body=screenWelcome();
  else if(x.t==='finish')body=screenFinish();
  else if(x.t==='actintro')body=screenActIntro(acts()[x.a],x.a);
  else if(x.t==='raise')body=screenRaise(acts()[x.a]);
  else body=screenStop(acts()[x.a],acts()[x.a].stops[x.s],x.s,acts()[x.a].stops.length);
  document.getElementById('body').innerHTML=body;

  const n=allStops().length;
  document.getElementById('prog').style.width=(100*answered()/n)+'%';
  document.getElementById('count').textContent=answered()+' of '+n;

  const nav=document.getElementById('nav');
  if(S.mode==='doc'){nav.style.display='none';return}
  nav.style.display='block';
  document.getElementById('back').disabled=i<=0;
  const f=document.getElementById('fwd');
  f.disabled=i>=all.length-1;
  f.textContent=x.t==='welcome'?'Begin':(i<all.length-1?'Next':'Done');
}

/* Installing as an application. A page opened from a file cannot be installed —
   that needs a service worker, and a service worker needs an origin. So the page
   does not offer it and does not pretend to: the button appears only when the
   browser itself says installation is available, which happens when the file is
   hosted. Saved to disk and double-clicked, everything here still works,
   offline, permanently. */
let installPrompt=null;
window.addEventListener('beforeinstallprompt',function(e){
  e.preventDefault();installPrompt=e;
  const b=document.getElementById('install');if(b)b.style.display='inline-flex';
});
window.addEventListener('appinstalled',function(){
  installPrompt=null;const b=document.getElementById('install');if(b)b.style.display='none';
});

document.addEventListener('click',function(ev){
  const t=ev.target;
  if(t.dataset&&t.dataset.act==='install'){
    if(!installPrompt)return;
    installPrompt.prompt();installPrompt=null;t.style.display='none';return;
  }
  const mic=t.closest?t.closest('[data-mic]'):null;
  if(mic){dictate(mic);return}
  if(t.id==='back'){goto2(stepIndex()-1);return}
  if(t.id==='fwd'){goto2(stepIndex()+1);return}
  if(t.dataset&&t.dataset.act==='export'){exportFile();return}
  if(t.dataset&&t.dataset.act==='doc'){S.mode='doc';render();window.scrollTo({top:0});return}
  if(t.dataset&&t.dataset.act==='guided'){S.mode='walk';render();window.scrollTo({top:0});return}
  if(t.classList.contains('ans')){
    const x=steps()[stepIndex()];
    const s=acts()[x.a].stops[x.s];
    S.answers[s.key]=S.answers[s.key]||{};
    S.answers[s.key].response=t.dataset.ans;
    persist();render();return;
  }
  if(t.classList.contains('rk')){
    const bx=t.closest('[data-raise]');S._draft=S._draft||{};
    S._draft[bx.dataset.raise]=S._draft[bx.dataset.raise]||{};
    S._draft[bx.dataset.raise].kind=t.dataset.kind;
    bx.querySelectorAll('.rk').forEach(function(b){b.classList.remove('sel')});
    t.classList.add('sel');return;
  }
  if(t.classList.contains('radd')){
    const bx=t.closest('[data-raise]'),act=bx.dataset.raise;
    S._draft=S._draft||{};const d=S._draft[act]||{};
    d.title=(bx.querySelector('.rtitle').value||'').trim();
    d.detail=(bx.querySelector('.rdetail').value||'').trim();
    if(!d.kind){alert('Choose what kind of thing this is first.');return}
    if(!d.title){alert('It needs a line saying what is missing or wrong.');return}
    if(d.detail.split(/\\s+/).filter(Boolean).length<8){
      alert('It needs a little more detail. Whoever picks this up will not have been in the room.');return}
    S.raised.push({act:act,kind:d.kind,title:d.title,detail:d.detail});
    delete S._draft[act];persist();render();return;
  }
});

document.addEventListener('input',function(ev){
  const t=ev.target;
  const bx=t.closest?t.closest('[data-raise]'):null;
  if(bx){S._draft=S._draft||{};S._draft[bx.dataset.raise]=S._draft[bx.dataset.raise]||{};
    if(t.classList.contains('rtitle'))S._draft[bx.dataset.raise].title=t.value;
    if(t.classList.contains('rdetail'))S._draft[bx.dataset.raise].detail=t.value;
    return}
  const x=steps()[stepIndex()];
  if(x.t!=='stop')return;
  const s=acts()[x.a].stops[x.s];
  S.answers[s.key]=S.answers[s.key]||{};
  if(t.classList.contains('reason'))S.answers[s.key].reason=t.value;
  if(t.classList.contains('choice'))S.answers[s.key].choice=t.value;
  clearTimeout(window._pt);window._pt=setTimeout(persist,600);
});

document.addEventListener('keydown',function(ev){
  if(ev.target.tagName==='TEXTAREA')return;
  if(ev.key==='ArrowRight')goto2(stepIndex()+1);
  if(ev.key==='ArrowLeft')goto2(stepIndex()-1);
});

(function(){
  const saved=restore();
  if(saved&&(Object.keys(saved.answers||{}).length+(saved.raised||[]).length)>0){
    S.answers=saved.answers||{};S.raised=saved.raised||[];
    S.act=saved.act||0;S.stop=saved.stop==null?-1:saved.stop;S.mode=saved.mode||'walk';
    const el=document.getElementById('resumed');if(el)el.style.display='block';
  }
  render();
})();
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
        # An identifier is capitalised wherever it stands; its plain-language name
        # is not. Substituting one for the other at the start of a sentence gives
        # "A site census. the question of ..." — which reads as a typo and makes
        # the reviewer distrust the rest of the page.
        before = text[:match.start()].rstrip()
        if not before or before[-1] in ".?!\n":
            return name[:1].upper() + name[1:]
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


# ---------------------------------------------------------------------------
# Positional keys, and the fingerprint that makes them safe
# ---------------------------------------------------------------------------
#
# The reviewer's page carries no station identifiers — that was the whole point
# of the language pass. But her export still has to be matched back to the
# stations it answers, or the walkthrough produces prose nobody can act on.
#
# So a stop is addressed by WHERE IT IS: act 3, stop 5 -> "a3s5". That leaks
# nothing. It is also fragile in exactly one way: if the journey changes between
# the page she was given and the build that reads her file, position 3/5 is a
# different question and her answer would be silently attached to it.
#
# The fingerprint closes that. It is a hash of the station order the page was
# built from, written into the export. A build that reads a file whose
# fingerprint does not match REFUSES rather than guessing, because a
# mis-attributed answer is worse than no answer: it puts words in her mouth.

TITLE = "QIPS Professional Programme"
SITTING = "Design walkthrough"

WELCOME = {
    "lede": "This is the whole design of the programme, laid out as a guided walk. "
            "It takes you through it part by part, and stops wherever a decision is "
            "still open or where what we have built needs testing against what you know.",
    "paragraphs": [
        "You are not being shown a finished thing for approval. Roughly two thirds of "
        "what follows is settled and built; the rest is deliberately unresolved, and "
        "each of those is here because it is better decided with you than presented to "
        "you. Where we have a view, you will see the view and the evidence under it.",
        "Nothing you do here changes the programme by itself. Your answers, with your "
        "reasons attached, become a proposal that a person reviews. A disagreement is "
        "as useful as an agreement — more useful, if it is early.",
        "It is long. It is meant to be taken in more than one sitting, and it saves "
        "itself as you go.",
    ],
}

FIELD_LABELS = {
    "what_we_built": "What is built",
    "reopening_note": "Reopening",
}

RAISE_KINDS = [
    ["MISSING_DECISION", "A decision that has to be taken and is not on this list at all."],
    ["MIS_FRAMED", "A question here that is asking the wrong thing."],
    ["WRONG_ASSUMPTION", "Something taken as given that does not hold in practice."],
    ["CONCERN", "Something that worries you and does not fit the other three."],
]

ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="7" fill="#1f4e79"/>'
    '<text x="16" y="22" font-family="sans-serif" font-size="15" font-weight="700" '
    'fill="#fff" text-anchor="middle">Q</text></svg>'
)


def pwa_manifest() -> dict[str, Any]:
    """What a browser needs before it will offer to install the page."""
    return {
        "name": f"{TITLE} — {SITTING}",
        "short_name": "QIPS walkthrough",
        "description": "A guided walk through the design of the programme.",
        "start_url": ".",
        "scope": ".",
        "display": "standalone",
        "background_color": "#f7f9fb",
        "theme_color": "#1f4e79",
        "icons": [
            {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
        ],
    }


# A worker whose only job is to make the page work with the network switched off.
# It caches the three files on install and answers from cache first, because
# nothing here changes between builds — a new build is a new deployment, and the
# version string below changes with it, which is what evicts the old cache.
SERVICE_WORKER = """const CACHE='qips-walkthrough-%(version)s';
const FILES=['.','index.html','manifest.webmanifest','icon.svg'];
self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).catch(()=>{}));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(
    ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
});
"""


# Buttons that are not <button>. Kept here rather than in CSS because it exists
# only to make a file input look like the control beside it.
SHELL_CSS = """
label.s{display:inline-flex;align-items:center;font-size:14.5px;padding:11px 20px;
  border-radius:9px;border:1px solid var(--line);background:var(--card);color:var(--muted)}
"""


def stop_key(act_index: int, stop_index: int) -> str:
    """Where a stop is, not what it is. Carries no internal identifier."""
    return f"a{act_index}s{stop_index}"


# A field repeated verbatim on this many stops of the same kind is a standing
# statement about that kind, not a fact about any one stop.
BOILERPLATE_AT = 5
FOLDABLE = ("what_we_built", "reopening_note")


def fold_boilerplate(acts: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Say a constant once, not twenty times.

    The generator writes each stop in full, which is right — a stop has to stand
    on its own in the export and in the blueprint. On the PAGE it reads
    differently: all twenty settled stops carried the same sentence about what is
    built, the same sentence about reopening, and the same invitation, so the
    single line that actually varied — the statement being reviewed — arrived
    fourth, under sixty words the reviewer had already read nineteen times.

    Anything identical across five or more stops of the same kind is lifted out
    and stated where it frames the reading: once on the opening page, and once at
    the top of each part that contains such stops. Nothing is lost, and the
    threshold is a count rather than a list of field names to maintain — if the
    generator later gives these stops distinct text, they stop being boilerplate
    on their own.
    """
    stops = [s for act in acts for s in act["stops"]]
    folded: dict[str, dict[str, str]] = {}

    for code in {(s.get("needs") or {}).get("code") for s in stops} - {None}:
        group = [s for s in stops if (s.get("needs") or {}).get("code") == code]
        for field in FOLDABLE:
            values = [s[field] for s in group if s.get(field)]
            if len(values) >= BOILERPLATE_AT and len(set(values)) == 1:
                folded.setdefault(code, {})[field] = values[0]
                for stop in group:
                    stop.pop(field, None)
    return folded


def renderable_acts(acts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The acts the page will actually show, in the order it will show them.

    The page hides an act with no stops. That is right for the empty catch-all
    and wrong for anything else — an act with a narrative and no stops would
    vanish silently, taking its narrative with it. Python decides here, once, so
    that the keys assigned below and the steps the browser walks cannot diverge.
    """
    keep = []
    for act in acts:
        if act.get("stops"):
            keep.append(act)
        elif not act.get("catch_all"):
            raise WalkthroughError(
                f"{act.get('id')} ('{act.get('title')}') has no stops. The page hides an "
                f"empty act, so its narrative would disappear without anyone deciding to "
                f"remove it. Either anchor stations to it or delete it from the spine."
            )
    return keep


def journey_fingerprint(acts: list[dict[str, Any]]) -> str:
    """A hash of the station order this page was built from."""
    spine = "|".join(stop["id"] for act in renderable_acts(acts) for stop in act["stops"])
    return hashlib.sha256(spine.encode("utf-8")).hexdigest()[:16]


def resolve_responses(payload: dict[str, Any], acts: list[dict[str, Any]]) -> dict[str, Any]:
    """Turn positional keys back into station ids, or refuse.

    Refusing is the feature. If the journey has moved under the export, every
    answer after the change would attach to the wrong question, and the result
    would look entirely plausible.
    """
    shown = renderable_acts(acts)
    expected = journey_fingerprint(acts)
    got = payload.get("journey_fingerprint")
    if got != expected:
        raise WalkthroughError(
            f"this response file was produced from a different version of the walkthrough "
            f"(it carries {got!r}, this build is {expected!r}). The answers are positional, "
            f"so reading them against a changed journey would attach them to the wrong "
            f"questions. Rebuild the page from the version she was sent, or ask for a fresh "
            f"pass — do not reconcile these by hand."
        )
    index = {stop_key(ai, si): stop["id"]
             for ai, act in enumerate(shown) for si, stop in enumerate(act["stops"])}
    out: dict[str, Any] = {}
    for item in payload.get("responses") or []:
        station = index.get(item.get("station"))
        if not station:
            raise WalkthroughError(
                f"the response file names a stop {item.get('station')!r} that this journey "
                f"does not have"
            )
        out[station] = {k: v for k, v in item.items() if k != "station"}
    return out


def build_html(acts: list[dict[str, Any]], stations: list[dict[str, Any]], commit: str,
               hosted: bool = False) -> str:
    lang = load_language()
    # Filtering happens BEFORE redaction, while `catch_all` still exists — the JS
    # used to do it, and `catch_all` is redacted away, so the page rendered a
    # blank final act. A regression the stop-count test could not see, because
    # the act had no stops to count.
    shown = renderable_acts(acts)
    fingerprint = journey_fingerprint(acts)

    # Everything below this line is what a committee member will actually read.
    view = reviewer_view(shown, lang)
    # Positional keys are attached AFTER redaction, so they cannot be translated
    # or stripped by it. Same order, same length — reviewer_view is structural.
    for act_index, act in enumerate(view):
        for stop_index, stop in enumerate(act["stops"]):
            stop["key"] = stop_key(act_index, stop_index)
    boilerplate = fold_boilerplate(view)

    data = {
        "acts": view,
        "boilerplate": boilerplate,
        "fieldLabels": FIELD_LABELS,
        "title": TITLE,
        "sitting": SITTING,
        "commit": commit,
        "journey_fingerprint": fingerprint,
        "welcome": WELCOME,
        "raiseKinds": RAISE_KINDS,
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

    total = sum(len(act["stops"]) for act in view)
    icon = urllib.parse.quote(ICON_SVG, safe="")
    if hosted:
        # Served from an origin: the manifest and the worker are real files, and
        # the browser will offer to install the page as an application.
        head_extra = '<link rel="manifest" href="manifest.webmanifest">'
        register = ("<script>if('serviceWorker' in navigator)"
                    "window.addEventListener('load',function(){"
                    "navigator.serviceWorker.register('sw.js').catch(function(){})});</script>")
    else:
        # Opened from a file: a worker cannot register, so none is attempted. The
        # manifest still travels inside the page, which costs nothing and means a
        # hosted copy of this exact file is installable without a rebuild.
        head_extra = ('<link rel="manifest" href="data:application/manifest+json,'
                      + urllib.parse.quote(json.dumps(pwa_manifest()), safe="") + '">')
        register = ""

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{TITLE} — {SITTING}</title>
<meta name="description" content="A guided walk through the design of the {TITLE},
part by part, stopping wherever a decision is still open.">
<meta name="theme-color" content="#1f4e79">
<link rel="icon" href="data:image/svg+xml,{icon}">
{head_extra}
<style>{CSS}{SHELL_CSS}</style></head><body>
<div class="warnbar">A draft for discussion. Nothing here is decided, published or final.</div>
<div class="top"><div class="inner">
  <div class="brand">{TITLE}<span>Cohort 1 &middot; SQHN and Partners</span></div>
  <div class="bar"><i id="prog"></i></div>
  <div class="count" id="count">0 of {total}</div>
  <div class="saved" id="saved">saved</div>
</div></div>
<main id="body"></main>
<div class="nav" id="nav"><div class="inner">
  <button class="s" id="back">Back</button>
  <span class="spacer"></span>
  <span class="quiet" id="resumed" style="display:none">Picked up where you left off</span>
  <button class="s" id="install" data-act="install" style="display:none"
    title="Install this as an application on this device">Install</button>
  <button class="s" data-act="export" title="Download your answers so far as a file">Save a copy</button>
  <label class="s" style="cursor:pointer">Load a copy
    <input type="file" accept="application/json" onchange="importFile(event)" style="display:none"></label>
  <button class="p" id="fwd">Next</button>
</div></div>
<script>const DATA={payload};</script>
<script>{JS}</script>
{register}
</body></html>
"""


def to_capture(payload: dict[str, Any], acts: list[dict[str, Any]]) -> dict[str, Any]:
    """Her file, in the form the blueprint compiler reads.

    Two tools, one boundary. This module owns the positional scheme, because it
    invented it to keep identifiers off her page; the compiler owns what a
    decision means. Neither has to know the other's business, and the conversion
    is the only place the two vocabularies meet — which is also the only place
    the fingerprint can be checked, so it is checked here.
    """
    resolved = resolve_responses(payload, acts)
    return {
        "sitting": payload.get("sitting") or SITTING,
        "responses": [dict(body, station=station) for station, body in resolved.items()],
        "raised": payload.get("raised") or [],
    }


def write_pwa(directory: Path, acts: list[dict[str, Any]], stations: list[dict[str, Any]],
              commit: str) -> list[Path]:
    """Write the hosted form: the same page, plus what makes it installable.

    Four files, all static, no build step and no server code — it can go on any
    static host, including whatever the programme ends up using. The single-file
    build stays the default and stays the thing that is sent by email; this is
    what turns it into something with an icon on her dock.
    """
    directory.mkdir(parents=True, exist_ok=True)
    page = build_html(acts, stations, commit, hosted=True)
    version = hashlib.sha256(page.encode("utf-8")).hexdigest()[:12]
    files = {
        "index.html": page,
        "manifest.webmanifest": json.dumps(pwa_manifest(), indent=2),
        "icon.svg": ICON_SVG,
        "sw.js": SERVICE_WORKER % {"version": version},
    }
    written = []
    for name, body in files.items():
        path = directory / name
        path.write_text(body, encoding="utf-8")
        written.append(path)
    return written


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

    # The page must be self-contained: no request, at any point, to anything that
    # is not inside the file. That is what makes it work offline, on a plane, in
    # a hospital with no wifi — and it is the property most easily lost by
    # accident, because a font or an icon set looks free.
    for external in ("<script src=", "<link rel=\"stylesheet\"", "@import", "src=\"http", "url(http"):
        if external in html_out:
            failures.append(f"page loads an external resource ({external}); it must be self-contained")

    # Autosave, deliberately. See the note at the top of this file — the earlier
    # rule was the opposite, and this test is inverted rather than deleted so
    # that the reversal is visible to whoever reads it next. Losing an hour of
    # the reviewer's thinking costs more than a storage-free page is worth.
    if "localStorage" not in html_out:
        failures.append(
            "the page does not save progress. Pausing and coming back is a stated "
            "requirement; without it, closing the tab loses everything."
        )
    # Autosave is per-browser and per-device. It is a convenience, never the only
    # copy — so the export must survive alongside it.
    if "journey_fingerprint" not in html_out:
        failures.append("responses can be exported without the fingerprint that makes them readable")

    # Every station must still REACH the page — but not by its identifier, which
    # is now deliberately withheld. Counting the rendered stops proves presence
    # without reintroducing the leak this design exists to close.
    try:
        payload = json.loads(re.search(r"const DATA=(\{.*\});</script>", html_out, re.S).group(1))
        rendered = sum(len(act.get("stops", [])) for act in payload["acts"])
    except Exception as exc:
        failures.append(f"could not parse the page payload to count stops: {exc}")
        payload = None
    else:
        if rendered != len(stations):
            failures.append(
                f"{len(stations)} stations generated but {rendered} reached the page"
            )

    # --- positional keys and the fingerprint -------------------------------
    if payload:
        keys = [stop.get("key") for act in payload["acts"] for stop in act["stops"]]
        if any(k is None for k in keys):
            failures.append("a stop reached the page with no key; her answer could not be matched back")
        if len(set(keys)) != len(keys):
            failures.append("two stops share a key; one answer would overwrite the other")

        # The round trip must work, and must refuse when the journey has moved.
        export = {"journey_fingerprint": payload["journey_fingerprint"],
                  "responses": [{"station": keys[0], "response": "ACCEPT", "reason": ""},
                                {"station": keys[-1], "response": "CHALLENGE", "reason": "no"}]}
        try:
            resolved = resolve_responses(export, acts)
        except WalkthroughError as exc:
            failures.append(f"a valid response file was refused: {exc}")
        else:
            first = renderable_acts(acts)[0]["stops"][0]["id"]
            if first not in resolved:
                failures.append(
                    f"the first stop resolved to {sorted(resolved)} rather than {first}; "
                    f"positional keys are not being mapped back to the questions they answer"
                )
        stale = dict(export, journey_fingerprint="0000000000000000")
        try:
            resolve_responses(stale, acts)
        except WalkthroughError:
            pass
        else:
            failures.append(
                "a response file from a different journey was accepted. Its answers would be "
                "attached to whatever question now sits in each position — silently, and "
                "plausibly."
            )

    # The conversion the compiler reads must produce station ids it knows, or her
    # answers arrive at a compiler that silently skips what it cannot place.
    if payload:
        keys = [stop["key"] for act in payload["acts"] for stop in act["stops"]]
        capture = to_capture(
            {"journey_fingerprint": payload["journey_fingerprint"],
             "responses": [{"station": k, "response": "ACCEPT", "reason": ""} for k in keys],
             "raised": []},
            acts)
        known = {s["id"] for s in stations}
        stray = [r["station"] for r in capture["responses"] if r["station"] not in known]
        if stray:
            failures.append(f"the conversion produced stops the compiler does not know: {stray[:3]}")
        if len(capture["responses"]) != len(stations):
            failures.append(
                f"{len(stations)} answers went in and {len(capture['responses'])} came out"
            )

    # --- the guided walk ---------------------------------------------------
    # She must not need anyone to explain the page to her. Each of these is a
    # thing a narrator would otherwise have had to say out loud.
    for marker, missing in [
        ("screenWelcome", "the page never introduces itself"),
        ("screenActIntro", "parts begin without saying what they are about"),
        ("screenFinish", "the walk has no ending, so she cannot tell when she is done"),
        ("screenDoc", "there is no way to read the whole thing straight through"),
        ("data-mic", "there is no way to speak an answer instead of typing it"),
        ("id=\"back\"", "there is no way to go back"),
        ("id=\"prog\"", "there is no indication of how far in she is"),
        ("rel=\"manifest\"", "the page cannot be installed as an application"),
    ]:
        if marker not in html_out:
            failures.append(f"guided walk: {missing}")

    # --- the two builds ----------------------------------------------------
    # The file build must attempt no worker: registration always fails from
    # file://, and a console error on open is how a reviewer learns to distrust
    # a page. The hosted build must attempt one, or it will never install.
    if "serviceWorker" in html_out:
        failures.append(
            "the single-file build tries to register a service worker. It cannot from "
            "file://, so this only produces an error the reviewer will see."
        )
    hosted = build_html(acts, stations, "self-test", hosted=True)
    if "serviceWorker" not in hosted or "sw.js" not in hosted:
        failures.append("the hosted build registers no worker, so it can never be installed")
    if "data:application/manifest" in hosted:
        failures.append("the hosted build still carries an inline manifest instead of the file")
    if "beforeinstallprompt" not in html_out:
        failures.append("nothing listens for the browser's offer to install")

    with tempfile.TemporaryDirectory() as tmp:
        written = {p.name for p in write_pwa(Path(tmp) / "site", acts, stations, "self-test")}
        if written != {"index.html", "manifest.webmanifest", "icon.svg", "sw.js"}:
            failures.append(f"the hosted build wrote {sorted(written)}")
        else:
            cached = (Path(tmp) / "site/sw.js").read_text(encoding="utf-8")
            for needed in ("index.html", "manifest.webmanifest", "icon.svg"):
                if needed not in cached:
                    failures.append(f"the worker does not cache {needed}; offline use would break")


    # Every stop must say what it needs FROM her. A stop with no badge is a stop
    # she has to guess the purpose of.
    if payload:
        unbadged = [act["title"] for act in payload["acts"]
                    for stop in act["stops"] if not (stop.get("needs") or {}).get("label")]
        if unbadged:
            failures.append(
                f"{len(unbadged)} stop(s) do not say what they need from the reviewer "
                f"(in: {', '.join(sorted(set(unbadged))[:3])})"
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
    # a name substituted at the start of a sentence must be capitalised
    opening = translate("A site census is needed. Q001 is the other unknown.", lang)
    if ". " in opening and re.search(r"\.\s+[a-z]", opening):
        failures.append(f"translation left a sentence starting in lower case: {opening!r}")

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
    print(f"walkthrough self-test: all checks passed — {len(stations)} stops, "
          f"{len(renderable_acts(acts))} acts{note}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="write the single self-contained file")
    parser.add_argument("--pwa", metavar="DIR",
                        help="write the hosted form: page, manifest, icon and worker")
    parser.add_argument("--responses", metavar="FILE",
                        help="a file saved from the page; converts it for the blueprint compiler")
    parser.add_argument("--capture-out", metavar="FILE", default="capture.yaml")
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

    if args.responses:
        payload = json.loads(Path(args.responses).read_text(encoding="utf-8"))
        try:
            capture = to_capture(payload, acts)
        except WalkthroughError as exc:
            print(f"  REFUSED  {exc}", file=sys.stderr)
            return 1
        Path(args.capture_out).write_text(
            yaml.dump(capture, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        print(f"read {len(capture['responses'])} response(s) and "
              f"{len(capture['raised'])} raised item(s) -> {args.capture_out}")
        print(f"\nnext: python3 engine/decision_interview.py --capture {args.capture_out} "
              f"--sitting <date>")
        return 0

    if args.check or not (args.out or args.pwa):
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
        if not (args.out or args.pwa):
            return 0

    if problems:
        for problem in problems:
            print(f"  FAIL  {problem}", file=sys.stderr)
        return 1

    if args.out:
        Path(args.out).write_text(build_html(acts, stations, args.commit), encoding="utf-8")
        print(f"wrote {args.out}")
    if args.pwa:
        for path in write_pwa(Path(args.pwa), acts, stations, args.commit):
            print(f"wrote {path}")
        print("\nServe that directory over http(s) and the browser will offer to install it.\n"
              "Opened straight from disk it still works, offline — it just cannot install,\n"
              "because installing needs a service worker and a worker needs an origin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
