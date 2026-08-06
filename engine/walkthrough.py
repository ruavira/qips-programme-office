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
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import warnings
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
  color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased;
  /* Every surface here renders text she typed or pasted, and a pasted URL is a
     single unbreakable word. Without this, one long link pushed the layout
     52,000 pixels wide and everything ran off the side of the screen. Set on
     the body so it inherits everywhere rather than being remembered per card. */
  overflow-wrap:anywhere}
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
.sendstate{font-size:12px;color:var(--faint);white-space:nowrap}
.sendstate.sent,.sendstate.final{color:var(--ok)}
/* Not green. It went, but nothing confirmed it, and a green tick would be the
   page asserting something it does not know. */
.sendstate.unconfirmed{color:var(--open)}
.sendstate.failed{color:var(--warn);font-weight:600}

main{max-width:820px;margin:0 auto;padding:38px 24px 150px}

h1{font-size:34px;line-height:1.15;letter-spacing:-.022em;margin-bottom:14px}
h2{font-size:27px;line-height:1.2;letter-spacing:-.018em;margin-bottom:10px}
h3{font-size:17px;margin-bottom:8px}
/* A section inside a card is a level-two heading — it sits directly under the
   page's h1 — but it should not LOOK like the 27px h2 that titles a part. A
   screen reader reads the level; a sighted reader reads the size. */
.sec{font-size:17px;line-height:1.35;letter-spacing:0;margin-bottom:8px}
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
.rec.stale{background:var(--bg);border-left-color:var(--faint);opacity:.85}
.rec.stale .k{color:var(--faint)}
.contested{background:var(--make-soft);border-left:3px solid var(--make);padding:16px 19px;
  border-radius:0 8px 8px 0;margin:16px 0}
.contested>.k{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--make);
  font-weight:650;margin-bottom:8px}
.contested .v{font-size:15.5px}
.position{background:var(--card);border:1px solid var(--line);border-radius:9px;
  padding:13px 15px;margin:12px 0}
.position .k{font-size:12.5px;font-weight:700;color:var(--ink);margin-bottom:6px;
  letter-spacing:0;text-transform:none}
.position .v.against{margin-top:7px;color:var(--muted);font-size:14.5px}
.want{margin-top:14px;padding-top:12px;border-top:1px dashed var(--make);font-size:15px}
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
.n-HELP_US_SETTLE_IT{background:var(--make-soft);color:var(--make)}
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

/* Note the direct-child selector. Written as `.legend div` it also matched the
   standing note NESTED inside each row, turning that note into its own flex
   container and stacking "What is built." one word per line. It read as a broken
   page and was invisible to every check in this file, because nothing here
   renders CSS. A screenshot found it. */
.legend>div{font-size:14px;color:var(--muted);margin:12px 0;display:grid;
  grid-template-columns:minmax(0,215px) minmax(0,1fr);gap:14px;align-items:start}
/* The badge is nowrap everywhere else, because beside a heading it should stay on
   one line. In this column it must wrap, or "we are not agreed — help us settle
   it" runs straight over the sentence next to it. */
.legend>div>.needs{justify-self:start;white-space:normal;line-height:1.45}
.legend .standingnote{margin-top:7px}
.legend .standingnote b{color:var(--ink)}

/* The opening page carries three things the rest of the walk does not: what
   success looks like, how much she is being asked to take on, and a way to say
   something that no question here asks for. Each gets its own shape so none of
   them reads as more of the same. */
.vision{background:var(--accent-soft);border:1px solid #d8e3f0;border-radius:12px;
  padding:20px 23px;margin:18px 0 4px}
.vision .k{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--accent);
  font-weight:650;margin-bottom:9px}
.vision ol{margin:0;padding:0;list-style:none;counter-reset:v}
.vision li{counter-increment:v;position:relative;padding-left:36px;margin:12px 0;font-size:15.5px}
.vision li:before{content:counter(v);position:absolute;left:0;top:1px;width:24px;height:24px;
  border-radius:50%;background:var(--accent);color:#fff;font-size:12px;font-weight:700;
  display:flex;align-items:center;justify-content:center}
.vision .close{margin:16px 0 0;font-size:14.5px;color:var(--muted);font-style:italic}

/* Everything that is not needed in order to begin lives behind this. It is a
   native <details>, so it works with no script, keyboard-reachable, and readable
   by a screen reader as the disclosure it is. */
details.more{background:var(--card);border:1px solid var(--line);border-radius:14px;
  box-shadow:var(--shadow);margin-bottom:18px}
details.more>summary{list-style:none;cursor:pointer;padding:18px 28px;font-size:15px;
  font-weight:650;color:var(--accent);display:flex;align-items:center;gap:10px}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::marker{content:''}
details.more>summary:before{content:'+';font-size:19px;font-weight:400;line-height:1;
  width:14px;text-align:center}
details.more[open]>summary:before{content:'\2212'}
details.more>summary:hover{text-decoration:underline}
.morebody{padding:0 28px 24px}
input.line{width:100%;max-width:340px;font-size:15.5px;padding:11px 14px;margin-top:12px;
  border:1px solid var(--line);border-radius:9px;background:var(--card)}
input.line:focus{outline:2px solid var(--accent-soft);border-color:var(--accent)}

.notestrip{border:1px dashed var(--line);border-radius:12px;padding:13px 17px;margin:2px 0 20px;
  background:var(--card)}
.notestrip.open{border-style:solid;border-color:var(--know);background:var(--know-soft)}
.notestrip .k{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--know);
  font-weight:650;margin-bottom:6px}
.notetoggle{border:0;background:none;padding:0;font-size:14.5px;color:var(--know);font-weight:600;
  text-align:left}
.notetoggle:hover{text-decoration:underline}
.notecount{margin-left:10px;font-size:13px}
.note-item{background:var(--card);border-left:3px solid var(--know);padding:11px 15px;
  border-radius:0 7px 7px 0;margin:10px 0;font-size:14.5px;white-space:pre-wrap}
.note-item .w{color:var(--faint);font-size:12.5px;margin-top:6px;white-space:normal}
.raised-item{background:var(--make-soft);border-left:3px solid var(--make);padding:11px 15px;
  border-radius:0 7px 7px 0;margin:9px 0;font-size:14.5px}
.raised-item b{color:var(--make)}
.doc .stopwrap{border-top:1px solid var(--line);padding-top:22px;margin-top:22px}
.warnbar{background:var(--open-soft);color:var(--open);padding:9px 24px;text-align:center;
  font-size:13px}
.warnbar.nosave{background:var(--warn-soft);color:var(--warn);font-weight:600}
/* Mobile is not a smaller desktop. Two things broke there and both were only
   visible in a narrow viewport: the needs badge sat beside the heading and ran
   off the right edge, and the navigation wrapped so that Back and Next landed on
   different rows. */
@media(max-width:640px){
  main{padding:24px 15px 186px} h1{font-size:26px} h2{font-size:21px}
  .sec{font-size:16.5px}
  .card{padding:19px 17px;border-radius:12px} .top .inner{padding:9px 14px;gap:11px}
  .brand span{display:none} .count{font-size:11.5px}
  .needs{white-space:normal}
  .legend>div{grid-template-columns:1fr;gap:8px}
  .vision{padding:16px 15px} .vision li{padding-left:31px}
  details.more>summary{padding:15px 17px} .morebody{padding:0 17px 19px}
  .stophead{flex-direction:column-reverse;gap:9px}
  .stophead .needs{margin-top:0;align-self:flex-start}
  #resumed{display:none}
  .nav .inner{padding:10px 14px;display:grid;grid-template-columns:1fr 1fr;gap:8px}
  .nav .spacer{display:none}
  #back{grid-area:1/1} #fwd{grid-area:1/2}
  .nav [data-act="export"]{grid-area:2/1} .nav label.s{grid-area:2/2}
  /* Install is display:none until the browser offers it. When it does appear
     it was auto-placed onto a third row that main's bottom padding did not
     allow for, hiding the end of the page behind the navigation. */
  #install{grid-area:3/1/auto/3}
  .nav button,.nav label.s{padding:11px 8px;justify-content:center;text-align:center;font-size:14px}
}
@media print{.top,.nav,.mic,.warnbar{display:none}.card{box-shadow:none;page-break-inside:avoid}}
"""

JS = r"""
const KEY='qips-ccc-walkthrough-v1';
let S={answers:{},raised:[],notes:[],path:null,act:0,stop:-1,mode:'welcome',reviewer:'',_draft:{}};

function esc(s){const d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}
/* The path filter. S.path null means nothing chosen yet, which is only true on the
   opening screen — every other screen is reached through a choice. */
function pathCodes(){
  const p=(DATA.paths||[]).find(function(x){return x.key===S.path});
  return p?p.codes:null;                       // null = no filter, show everything
}
function visible(stop){
  const codes=pathCodes();
  if(!codes)return true;
  return codes.indexOf((stop.needs||{}).code)>=0;
}
function acts(){
  return DATA.acts.map(function(a){return Object.assign({},a,{stops:(a.stops||[]).filter(visible)})})
                  .filter(function(a){return a.stops.length});
}
function allStops(){return acts().flatMap(a=>a.stops)}
function everyStop(){return DATA.acts.flatMap(function(a){return a.stops||[]})}
/* Counted against the chosen path, not against everything she has ever answered.
   If she walks the whole design and then narrows, "40 of 22" is nonsense; and if
   she widens, the answers she already gave still count. Nothing is discarded
   either way — the record sent back carries every answer regardless of which
   path is selected when it goes. */
function answered(){
  const on={};allStops().forEach(function(s){on[s.key]=1});
  return Object.keys(S.answers).filter(function(k){
    return on[k]&&S.answers[k]&&S.answers[k].response}).length;
}

/* Persistence. An earlier version deliberately held everything in memory and made
   the reviewer download a file. That was the wrong call once pausing and coming
   back became a requirement: losing an hour of someone's thinking costs far more
   than the tidiness of avoiding browser storage. Autosave is primary now; the
   file export stays, because storage is per-browser and she may want to send it.

   Storage is not always available. Private windows, "block all cookies", and some
   browsers' handling of pages opened straight from disk all refuse it. The first
   version of this caught the exception and carried on, which is the worst
   possible behaviour: the opening page PROMISED that answers save themselves, and
   then an hour of work disappeared on reload with nothing having gone visibly
   wrong. A page that cannot keep a promise must stop making it. */
function storageWorks(){
  try{
    const probe='__qips_probe__';
    localStorage.setItem(probe,'1');
    const back=localStorage.getItem(probe);
    localStorage.removeItem(probe);
    return back==='1';
  }catch(e){return false}
}
let CAN_SAVE=storageWorks();

function announceNoAutosave(){
  const bar=document.getElementById('nosave');
  if(bar)bar.style.display='block';
}
/* Two tabs.

   Storage is shared across every tab of the same browser, and each tab holds its
   own copy of the answers in memory. Writing that copy out wholesale means the
   last tab to save wins and the other one's work is gone — proved: three answers
   in one tab, one answer in a second, one answer left in storage. No error, no
   warning, no way for her to know. She opens the emailed link a second time
   without thinking about it and an hour disappears.

   So a save is a MERGE rather than a replacement. It re-reads what is on disk
   and unions it with what is in memory. That is safe here because nothing in
   this page ever deletes: an answer is set or changed, notes and raised items
   are only ever appended. Where both tabs touched the same stop, the tab doing
   the saving wins, which is the one she is actually looking at.

   Position — which part, which stop, which length — is deliberately NOT merged.
   That is per-tab and belongs to whichever tab last moved. */
function mergeSaved(prev){
  if(!prev||typeof prev!=='object')return {answers:S.answers,raised:S.raised,notes:S.notes||[]};
  const answers={};
  const prior=(prev.answers&&typeof prev.answers==='object'&&!Array.isArray(prev.answers))
    ?prev.answers:{};
  Object.keys(prior).forEach(function(k){if(prior[k]&&typeof prior[k]==='object')answers[k]=prior[k]});
  Object.keys(S.answers).forEach(function(k){answers[k]=S.answers[k]});   // this tab wins on collision
  const seen={},list=[];
  function add(arr,key){(Array.isArray(arr)?arr:[]).forEach(function(x){
    if(!x||typeof x!=='object')return;
    const id=key(x); if(seen[id])return; seen[id]=1; list.push(x)})}
  const rk=function(r){return [r.act,r.kind,r.title,r.detail].join('')};
  add(prev.raised,rk); add(S.raised,rk);
  const raised=list.slice();
  const seen2={},notes=[];
  (Array.isArray(prev.notes)?prev.notes:[]).concat(S.notes||[]).forEach(function(n){
    if(!n||typeof n!=='object')return;
    const id=[n.text,n.where].join(''); if(seen2[id])return; seen2[id]=1; notes.push(n)});
  return {answers:answers,raised:raised,notes:notes};
}

function persist(){
  if(!CAN_SAVE)return;
  try{
    const merged=mergeSaved(restore());
    S.answers=merged.answers;S.raised=merged.raised;S.notes=merged.notes;
    localStorage.setItem(KEY,JSON.stringify({answers:S.answers,raised:S.raised,
      notes:S.notes||[],path:S.path||null,
      act:S.act,stop:S.stop,mode:S.mode,reviewer:S.reviewer||'',
      at:new Date().toISOString()}));
    const el=document.getElementById('saved');
    if(el){el.classList.add('on');clearTimeout(window._st);
      window._st=setTimeout(function(){el.classList.remove('on')},1400);}
  }catch(e){
    // Storage worked at startup and has stopped — a full quota, most likely.
    // Silence here would be the same failure as before, one hour later.
    CAN_SAVE=false;announceNoAutosave();render();
  }
}
function restore(){
  if(!CAN_SAVE)return null;
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
/* The microphone is an icon and nothing else, so without a name of its own a
   screen reader announces it as "button" and there is no way to know what it
   does. aria-label rather than title alone: a title is a mouse-hover tooltip
   that assistive technology is not obliged to read. */
function box(cls,ph,val,min){
  const label=SR?'Speak instead of typing':'Dictation needs Chrome, Edge or Safari';
  return '<div class="ta"><textarea class="'+cls+'" placeholder="'+esc(ph)+'"'+
    (min?' style="min-height:'+min+'"':'')+'>'+esc(val||'')+'</textarea>'+
    '<button class="mic" data-mic="1" aria-label="'+esc(label)+'" title="'+esc(label)+'"'+
    (SR?'':' disabled')+
    '>'+MIC+'</button></div>';
}

/* Statements that are true of a whole kind of stop rather than of any one stop.
   Python lifts them out; they are shown on the opening page and once at the top
   of each part that contains such stops. */
function standing(code){
  const b=(DATA.boilerplate||{})[code];if(!b)return '';
  let h='';
  Object.keys(b).forEach(function(f){
    h+='<div class="standingnote"><b>'+esc(DATA.fieldLabels[f]||f)+'.</b> '+esc(b[f])+'</div>'});
  return h;
}

/* How many stops a given path contains. Counted from the WHOLE journey, not from
   the filtered one, or each button would report the length of the path already
   chosen rather than its own. */
function countFor(codes){
  return everyStop().filter(function(s){
    return !codes||codes.indexOf((s.needs||{}).code)>=0}).length;
}

/* The opening page answers four questions in the order somebody actually asks
   them: what is this for, what is it, what do you want from me, and how much of
   my time does it take. The last one is a choice rather than an announcement —
   52 stops handed to a busy person with no way to scale it is a demand, and the
   demand was the thing most likely to stop this being read at all. */
/* The opening page.

   The first version of this put a decision in front of the Begin button and
   greyed the button out until it was made — which is the same demand the paths
   were introduced to remove, wearing a different hat. Measured, it was 887 words
   and 3.7 phone screens before she could start, a third of it a legend
   explaining six question types she had not met yet.

   So: a default she can change rather than a gate she has to clear, and only
   what she needs in order to begin. Everything else is one disclosure away, and
   the legend is explained again in context at the top of every part, where she
   actually meets the badges. */
function screenWelcome(){
  const every=everyStop(),k={};
  every.forEach(function(s){if(s.needs)k[s.needs.code]=(k[s.needs.code]||0)+1});
  let h='<div class="card"><div class="eyebrow">'+esc(DATA.sitting)+'</div>';
  h+='<h1>'+esc(DATA.title)+'</h1>';
  const v=DATA.vision;
  if(v){
    h+='<div class="vision"><div class="k">'+esc(v.heading)+'</div>';
    h+='<p class="quiet" style="font-size:15.5px;margin-bottom:2px">'+esc(v.lede)+'</p><ol>';
    (v.outcomes||[]).forEach(function(o){h+='<li>'+esc(o)+'</li>'});
    h+='</ol>';
    if(v.closing)h+='<p class="close">'+esc(v.closing)+'</p>';
    h+='</div>';
  }
  h+='</div>';
  h+='<div class="card"><h2 class="sec">What this is</h2>';
  h+='<p class="lede">'+esc(DATA.welcome.lede)+'</p>';
  DATA.welcome.paragraphs.forEach(function(t){h+='<p class="prose">'+esc(t)+'</p>'});
  h+='</div>';

  // The length: already chosen, changeable in one click, in either direction.
  const cur=(DATA.paths||[]).find(function(p){return p.key===S.path});
  h+='<div class="card"><h2 class="sec">How long it is</h2>'+
     '<p class="quiet">You are set to the shortest walk &mdash; the stops only you can answer. '+
     'Change it here whenever you like, in either direction. Nothing you have already answered '+
     'is ever lost, and the whole design stays readable either way.</p>'+
     '<div class="btns" style="margin-top:13px">';
  (DATA.paths||[]).forEach(function(p){
    const c=countFor(p.codes);
    h+='<button class="r'+(S.path===p.key?' sel':'')+'" data-path="'+esc(p.key)+'">'+
       esc(p.label)+' &middot; '+c+'</button>';
  });
  h+='</div>';
  if(cur)h+='<p class="quiet" style="margin-top:11px">'+esc(cur.blurb)+'</p>';
  h+='<p class="quiet" style="margin-top:13px">'+(CAN_SAVE
      ?'It saves as you go, so you can stop anywhere and come back to it. '
      :'<b>This browser will not let the page save on its own</b>, so use <b>Save a copy</b> '+
       'before you close the tab. ')+
     'Nothing you do here changes the programme by itself &mdash; your answers become a '+
     'proposal that a person reviews.</p></div>';

  // Everything else, out of the way of starting.
  h+='<details class="more"'+(S._moreOpen?' open':'')+
     '><summary>More about how this works</summary><div class="morebody">';
  h+='<h2 class="sec">What is being asked of you</h2>'+
     '<p class="quiet">Not one kind of thing. The questions differ in what they need from you, '+
     'and each says which it is where you meet it, so this is reference rather than '+
     'something to learn now.</p><div class="legend">';
  ['YOUR_KNOWLEDGE','YOUR_JUDGEMENT','HELP_US_SETTLE_IT','DESIGN_WITH_US','ARGUE_WITH_US',
   'CHALLENGE_IF_WRONG'].forEach(function(c){
      const ex=every.find(function(s){return s.needs&&s.needs.code===c});
      if(!ex)return;
      h+='<div><span class="needs n-'+c+'">'+esc(ex.needs.label)+'</span><span>'+
         esc(ex.needs.invitation)+' <b>('+(k[c]||0)+')</b>'+standing(c)+'</span></div>';
    });
  h+='</div>';
  h+='<h2 class="sec" style="margin-top:24px">The rest of it</h2><ul class="opts">'+
     '<li>You can go back and change anything, at any point.</li>'+
     '<li>Prefer to talk? Every box has a microphone.</li>'+
     '<li>At the foot of every page there is a box for anything else on your mind. '+
     'It does not have to be about the question in front of you.</li>'+
     (DATA.submit
       ?'<li>Your answers go back to the programme office as you work, part by part. '+
        'There is no final step to remember, and nothing to email.</li>'
       :'<li>When you are done, <b>Save a copy</b> downloads a file to send to the '+
        'programme office. Nothing leaves this browser on its own.</li>')+
     '<li>The last page reads the whole design straight through, whichever length you are on.</li>'+
     '</ul></div></details>';
  if(DATA.submit&&!(DATA.submit.reviewer||S.reviewer)){
    // A name is one short line. It had a microphone and a resizable box, which
    // is the furniture of an essay answer and made the last thing before Begin
    // look like work. Build with --reviewer and she is never asked at all.
    h+='<div class="card"><h2 class="sec">Who is walking this?</h2>'+
       '<p class="quiet">So your answers arrive with your name on them. Nothing else is collected.</p>'+
       '<input class="who line" placeholder="Your name" value="'+esc(S.reviewer||'')+'">'+
       '</div>';
  }
  return h;
}

/* Free text, everywhere.

   Every other input on this page is attached to a question we thought to ask,
   which means the page can only hear what it already anticipated. This one is
   attached to nothing. A thought she has at stop 14 does not have to wait for a
   stop that fits it, and does not have to be a decision, or finished, or about
   the thing in front of her.

   It records where she was when she wrote it, because "the coaching side is too
   thin" means something different on part 3 than on part 6, and she should not
   have to say which. */
function currentWhere(){
  const x=steps()[stepIndex()];
  if(!x)return 'Somewhere in the walk';
  if(x.t==='welcome')return 'The opening page';
  if(x.t==='finish')return 'The last page';
  const a=acts()[x.a];
  if(!a)return 'Somewhere in the walk';
  if(x.t==='actintro')return a.title;
  if(x.t==='raise')return a.title+' — the open question at the end';
  const s=a.stops[x.s];
  return a.title+' — ' +clip(s?s.prompt:'',90);
}
function noteStrip(){
  const mine=S.notes||[];
  let h='<div class="notestrip'+(S._noteOpen?' open':'')+'">';
  if(!S._noteOpen){
    h+='<button class="notetoggle" data-act="note">Something else on your mind? Say it here</button>';
    if(mine.length)h+='<span class="quiet notecount">'+mine.length+' kept so far</span>';
  }else{
    h+='<div class="k">Anything at all</div>'+
       '<p class="quiet" style="margin-bottom:12px">It does not have to be about this page, '+
       'or be a decision, or be finished. It comes back to us with where you were when you '+
       'wrote it, so we can put it in context.</p>'+
       box('notetext','What is on your mind?',S._noteDraft||'')+
       '<div class="btns" style="margin-top:11px">'+
       '<button class="p noteadd">Keep this</button>'+
       '<button class="s" data-act="noteback">Not now</button></div>';
    mine.slice().reverse().forEach(function(nt){
      h+='<div class="note-item">'+esc(nt.text)+
         '<div class="w">'+esc(nt.where)+'</div></div>'});
  }
  return h+'</div>';
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
  const u=r.under_review;
  if(u){
    h+='<div class="contested"><div class="k">This one is being reconsidered</div>';
    h+='<div class="v">'+esc(u.why)+'</div>';
    if(u.on_sustainability)h+='<div class="v" style="margin-top:10px">'+esc(u.on_sustainability)+'</div>';
    if(u.what_the_record_actually_shows)h+='<div class="v" style="margin-top:10px">'+
      '<b>How the figure was actually reached.</b> '+esc(u.what_the_record_actually_shows)+'</div>';
    if(u.what_is_genuinely_weak)h+='<div class="v" style="margin-top:10px">'+
      '<b>Where that reasoning is weak.</b> '+esc(u.what_is_genuinely_weak)+'</div>';
    if(u.what_reopening_would_take)h+='<div class="v" style="margin-top:10px">'+
      '<b>What changing it would take.</b> '+esc(u.what_reopening_would_take)+'</div>';
    if(u.what_the_research_found)h+='<div class="v" style="margin-top:10px">'+
      '<b>What we went and found out.</b> '+esc(u.what_the_research_found)+'</div>';
    (u.the_competing_positions||[]).forEach(function(pos,i){
      h+='<div class="position"><div class="k">Position '+(i+1)+' &mdash; '+esc(pos.name)+'</div>';
      if(pos.ladder)h+='<div class="v"><b>'+esc(pos.ladder)+'</b></div>';
      if(pos.case_for)h+='<div class="v" style="margin-top:7px">'+esc(pos.case_for)+'</div>';
      if(pos.case_against)h+='<div class="v against"><b>Against:</b> '+esc(pos.case_against)+'</div>';
      h+='</div>';
    });
    if(u.what_is_being_done)h+='<div class="v" style="margin-top:12px">'+esc(u.what_is_being_done)+'</div>';
    if(u.what_we_want_from_you)h+='<div class="want"><b>What would help most here.</b> '+
      esc(u.what_we_want_from_you)+'</div>';
    h+='</div>';
  }
  if(r.present){
    h+='<div class="rec'+(u?' stale':'')+'"><div class="k">'+
       (u?'The figure now under review — shown so you can see what it rested on'
         :'Our recommendation')+'</div>';
    if(r.option)h+='<div class="v"><b>'+esc(r.option)+'</b></div>';
    if(r.rationale)h+='<div class="v" style="margin-top:8px">'+esc(r.rationale)+'</div>';
    (r.comparators||[]).forEach(function(c){h+='<div class="ev">Comparator: '+esc(c)+'</div>'});
    (r.evidence||[]).forEach(function(e){h+='<div class="ev">Evidence: '+esc(e)+'</div>'});
    if(r.confidence)h+='<div class="ev">Confidence: '+esc(r.confidence)+
      (r.confidence_basis?' &mdash; '+esc(r.confidence_basis):'')+'</div>';
    if(r.what_would_change_it)h+='<div class="ev"><b>What would change this:</b> '+esc(r.what_would_change_it)+'</div>';
    h+='<div class="disc">'+(u
      ?'This is no longer put forward as our position. It is shown in full because the '+
       'reasoning is what you would need in order to disagree with it usefully.'
      :'A recommendation, not a decision. Only the committee decides.')+'</div></div>';
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
  const nn=(S.notes||[]).length;
  let h='<div class="card"><h1>That is the end of the walk</h1>';
  h+='<p class="lede">You answered '+a+' of '+n+' stops, raised '+S.raised.length+
     ' thing'+(S.raised.length===1?'':'s')+' we had not asked about'+
     (nn?', and left '+nn+' note'+(nn===1?'':'s'):'')+'.</p>';
  h+='<p class="prose">Nothing here has changed the programme. Your answers become a proposal with '+
     'your reasons attached, which a person reviews before anything is adopted. Anything you '+
     'skipped stays open, and the design continues to work either way.</p>';
  if(a<n)h+='<p class="quiet">'+(n-a)+' stop'+(n-a===1?'':'s')+' unanswered. That is a legitimate '+
     'outcome rather than an omission, and you can go back to any of them.</p>';
  if(S.path&&S.path!=='all'){
    const more=everyStop().length-n;
    if(more>0)h+='<p class="quiet">You took the shorter walk. There '+(more===1?'is':'are')+' '+
      more+' further stop'+(more===1?'':'s')+' you have not been shown, all of them already '+
      'settled or already recommended. If you have the appetite, go back to the opening page and '+
      'widen it &mdash; everything you have answered is kept.</p>';
  }
  h+='<div class="btns" style="margin-top:20px">';
  if(DATA.submit){
    h+='<button class="p" data-act="finalsend">Send my responses</button>'+
       '<button class="s" data-act="export">Also keep a copy</button>';
  }else{
    h+='<button class="p" data-act="export">Save my responses to a file</button>';
  }
  h+='<button class="s" data-act="doc">Read the whole thing as one document</button></div>';
  if(DATA.submit){
    h+='<p class="quiet" style="margin-top:14px">Your answers have been going back as you '+
       'worked, so nothing is lost either way. This marks the pass finished.</p>';
    // Said here rather than only in the status line, because this is the last
    // moment she is looking at the page and the only moment the doubt is cheap
    // to settle. Never phrased as an alarm — most of the time it has arrived.
    if((sendState==='sent'||sendState==='final')&&!sendConfirmed){
      h+='<p class="quiet" style="margin-top:10px"><b>One thing worth doing.</b> The site '+
         'accepted everything you sent, but did not acknowledge it the way a fully configured '+
         'form does. It has most likely arrived. If you would rather not rely on that, '+
         '<b>Also keep a copy</b> downloads the same record as a file &mdash; thirty seconds, '+
         'and the doubt is gone.</p>';
    }
  }else{
    h+='<p class="quiet" style="margin-top:14px">This downloads a file. Send it to the '+
       'programme office however suits you &mdash; it is the only copy outside this browser.</p>';
  }
  h+='</div>';
  if(nn){
    h+='<div class="card"><h2 class="sec">What was on your mind</h2>'+
       '<p class="quiet">Written where no question asked for it. These travel with everything else.</p>';
    S.notes.forEach(function(nt){
      h+='<div class="note-item">'+esc(nt.text)+'<div class="w">'+esc(nt.where)+'</div></div>'});
    h+='</div>';
  }
  if(S.raised.length){
    h+='<div class="card"><h2 class="sec">What you raised</h2>';
    S.raised.forEach(function(r){
      h+='<div class="raised-item"><b>'+esc(r.kind.replace(/_/g,' ').toLowerCase())+'</b> &mdash; '+
         esc(r.title)+'<div class="quiet" style="margin-top:5px">'+esc(r.detail)+'</div></div>'});
    h+='</div>';
  }
  return h;
}

function screenDoc(){
  let h='<div class="card"><h1>'+esc(DATA.title)+'</h1><p class="lede">'+esc(DATA.welcome.lede)+
        '</p><p class="quiet">This is everything, whichever path you chose. Nothing here is '+
        'hidden by that choice &mdash; it only decides what stops to ask you something.</p>'+
        '<button class="s" data-act="guided">Back to the guided walk</button></div>';
  DATA.acts.forEach(function(a,i){
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
  // A part boundary is the natural save point: she has finished a train of
  // thought, and if she stops here the programme office still has it.
  if(x.t==='actintro'||x.t==='raise'||x.t==='finish')sendNow(false);
  S.mode=x.t==='welcome'?'welcome':(x.t==='finish'?'finish':'walk');
  if(x.t==='actintro'){S.act=x.a;S.stop=-1}
  if(x.t==='stop'){S.act=x.a;S.stop=x.s}
  if(x.t==='raise'){S.act=x.a;S.stop=-2}
  persist();render();window.scrollTo({top:0});
}

/* Sending her answers back.

   The burden this removes: without it she must press Save a copy, find the file
   in Downloads, and attach it to an email — three steps at the end, when she is
   tired, and the one place where failure loses everything she did.

   Sending happens at each part boundary rather than only at the end, because the
   end is exactly the moment a tired person closes a tab. An interrupted pass is
   still a useful pass. It is also idempotent: the same answers are sent again
   rather than a diff, so the newest submission is always the whole picture and a
   lost one costs nothing.

   Nothing here is silent. A send that fails says so and retries; a send that has
   never succeeded says that too. She is never left believing her work travelled
   when it did not — the same rule as the autosave. */
/* One more thing this page cannot know, and therefore must not claim.

   Netlify returns no machine-readable receipt. A form it processed redirects to
   a success page; a POST to the same path when the form is NOT detected is
   served the page itself. Both arrive here as 200, so status alone cannot tell
   delivery from silence — and "form detection is off" is the single likeliest
   misconfiguration, the one the deploy runbook devotes a whole section to.

   Under the old code that case read as "sent to the programme office". She could
   work for an hour, be told at every part boundary that her answers had gone
   back, finish, close the tab, and have sent nothing at all. That is the exact
   failure the rest of this file is built to prevent, hiding behind a 2xx.

   The redirect is the only signal that distinguishes them, and it is not a
   documented contract. So it is treated as corroboration rather than proof:
   confirmed when it happened, honestly hedged when it did not. Being wrong in
   the hedging direction costs a redundant nudge to keep a copy. Being wrong the
   other way costs everything she wrote. */
let sentHash=null,sendState='idle',sendAt=null,sendConfirmed=false;

function payload(final){
  return {sitting:DATA.sitting,generated_from:DATA.commit,
    journey_fingerprint:DATA.journey_fingerprint,
    reviewer:(DATA.submit&&DATA.submit.reviewer)||S.reviewer||'',
    path:S.path||'',
    answered:answered(),of:allStops().length,final:!!final,
    responses:Object.keys(S.answers).filter(function(k){return S.answers[k].response})
      .map(function(k){return {station:k,response:S.answers[k].response,
        chosen_option:S.answers[k].choice||null,reason:S.answers[k].reason||''}}),
    notes:S.notes||[],
    raised:S.raised};
}
/* What a person sees in the inbox.

   The machine record has to travel — it is what the compiler reads and what
   carries the fingerprint. But it must not be the thing anyone READS. These two
   build the human view: one line that says who and how far, and a digest of what
   she actually said, in the order she said it. */
function clip(t,n){t=String(t||'').replace(/\s+/g,' ').trim();
  return t.length>n?t.slice(0,n-1)+'…':t}

function summaryLine(final){
  const a=answered(),n=allStops().length;
  const bits=[(DATA.submit&&DATA.submit.reviewer)||S.reviewer||'Someone unnamed',
    a+' of '+n+' answered'];
  if((S.notes||[]).length)bits.push(S.notes.length+' note'+(S.notes.length===1?'':'s'));
  if(S.raised.length)bits.push(S.raised.length+' thing'+(S.raised.length===1?'':'s')+' raised');
  bits.push(final?'finished':'still going');
  return bits.join(' · ');
}

function readable(){
  const lines=[];
  // Over the WHOLE journey, not the filtered one. If she answered something and
  // then narrowed her path, the answer still exists and still has to be read.
  const every=DATA.acts;
  every.forEach(function(a,ai){
    (a.stops||[]).forEach(function(st,si){
      const ans=S.answers[st.key];
      if(!ans||!ans.response)return;
      lines.push(ans.response+' — '+clip(st.prompt,140));
      lines.push('    part '+(ai+1)+' of '+every.length+', '+a.title+
                 (st.needs?' · '+st.needs.label.toLowerCase():''));
      if(ans.choice)lines.push('    chose: '+clip(ans.choice,300));
      if(ans.reason)lines.push('    because: '+clip(ans.reason,600));
      lines.push('');
    });
  });
  if((S.notes||[]).length){
    lines.push('ON HER MIND — written where no question asked for it');
    lines.push('');
    S.notes.forEach(function(nt){
      lines.push(clip(nt.text,900));
      lines.push('    at: '+clip(nt.where,140));
      lines.push('');
    });
  }
  if(S.raised.length){
    lines.push('RAISED — things we had not asked about');
    lines.push('');
    S.raised.forEach(function(r){
      lines.push(r.kind.replace(/_/g,' ').toLowerCase()+' — '+clip(r.title,140));
      lines.push('    '+clip(r.detail,600));
      lines.push('');
    });
  }
  if(!lines.length)lines.push('Nothing answered yet.');
  return lines.join('\n');
}

function digest(o){
  const s=JSON.stringify(o);let h=0;
  for(let i=0;i<s.length;i++){h=(h*31+s.charCodeAt(i))|0}
  return h;
}
function sendStatus(){
  const el=document.getElementById('sendstate');
  if(!el)return;
  if(!DATA.submit){el.style.display='none';return}
  el.style.display='';
  el.className='sendstate '+sendState+((sendState==='sent'||sendState==='final')&&!sendConfirmed
    ?' unconfirmed':'');
  el.textContent=sendState==='sending'?'sending…'
    :sendState==='sent'?(sendConfirmed?'sent to the programme office':'sent — not yet acknowledged')
    :sendState==='failed'?'not sent yet — will try again'
    :sendState==='final'?(sendConfirmed?'sent — thank you':'sent — not yet acknowledged')
    :'';
  el.title=(sendState==='sent'||sendState==='final')&&!sendConfirmed
    ?'The site accepted it but did not acknowledge it the way a processed form does. '+
     'It has most likely arrived; keeping a copy costs nothing and removes the doubt.':'';
}
function sendNow(final){
  if(!DATA.submit)return Promise.resolve(false);
  const body=payload(final);
  if(!body.responses.length&&!body.raised.length&&!final)return Promise.resolve(false);
  const h=digest(body);
  if(h===sentHash&&!final)return Promise.resolve(false);   // nothing has changed
  sendState='sending';sendStatus();
  let request;
  if(DATA.submit.mode==='netlify'){
    // URL-encoded, because Netlify Forms does not accept JSON.
    const f=new URLSearchParams();
    f.append('form-name',DATA.submit.form);
    // Order here is cosmetic; order in the static form is what Netlify reads.
    f.append('summary',summaryLine(final));
    f.append('responses',readable());
    f.append('reviewer',body.reviewer||'not given');
    f.append('progress',body.answered+' of '+body.of);
    f.append('final',body.final?'yes':'no');
    f.append('full_record_json',JSON.stringify(body));
    request=fetch(DATA.submit.url,{method:'POST',
      headers:{'Content-Type':'application/x-www-form-urlencoded'},body:f.toString()});
  }else{
    request=fetch(DATA.submit.url,{method:'POST',
      headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  }
  return request.then(function(r){
    if(!r.ok)throw new Error('HTTP '+r.status);
    // r.redirected is true only if the server sent the browser somewhere else,
    // which is what a form Netlify actually handled does. A POST it ignored is
    // answered with the static file at that path and no redirect.
    sendConfirmed=!!r.redirected;
    sentHash=h;sendAt=new Date();sendState=final?'final':'sent';sendStatus();return true;
  }).catch(function(){
    sendState='failed';sendConfirmed=false;sendStatus();return false;
  });
}

function exportFile(){
  const out={sitting:DATA.sitting,generated_from:DATA.commit,
    journey_fingerprint:DATA.journey_fingerprint,
    responses:Object.keys(S.answers).filter(function(k){return S.answers[k].response})
      .map(function(k){return {station:k,response:S.answers[k].response,
        chosen_option:S.answers[k].choice||null,reason:S.answers[k].reason||''}}),
    notes:S.notes||[],
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
    S.raised=d.raised||[];S.notes=d.notes||[];
    if(!S.path)S.path='all';
    persist();render();
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
  // The free-text box sits under every screen of the walk, which is what makes it
  // always available without adding a control to the navigation she has to learn.
  if(S.mode!=='doc')body+=noteStrip();
  document.getElementById('body').innerHTML=body;

  const n=allStops().length||1;
  document.getElementById('prog').style.width=(100*Math.min(answered(),n)/n)+'%';
  document.getElementById('count').textContent=answered()+' of '+allStops().length;

  const nav=document.getElementById('nav');
  if(S.mode==='doc'){nav.style.display='none';return}
  nav.style.display='block';
  document.getElementById('back').disabled=i<=0;
  const f=document.getElementById('fwd');
  // Never gated on the length. A default she can change is an offer; a disabled
  // button is a demand, and the demand was the thing this was meant to remove.
  // The count rides on the button so she knows what she is agreeing to at the
  // moment she agrees to it.
  f.disabled=i>=all.length-1;
  f.textContent=x.t==='welcome'?('Begin · '+allStops().length+' stops')
    :(i<all.length-1?'Next':'Done');
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
  // The path buttons carry child elements, so the click lands on a <b> or a
  // <span> as often as on the button itself.
  const pb=t.closest?t.closest('[data-path]'):null;
  if(pb){
    S.path=pb.dataset.path;
    // Changing the length must never strand her mid-walk on a stop the new one
    // filters out. The control lives on the opening page, so return there.
    S.mode='welcome';S.act=0;S.stop=-1;
    persist();render();
    // Keep the control she just used under her thumb rather than throwing her
    // back to the top of the page.
    const el=document.querySelector('[data-path].sel');
    if(el)el.scrollIntoView({block:'center'});
    return;
  }
  // A native <details> loses its open state when render() rewrites the body, so
  // it is remembered. Read after the browser has toggled it, not before.
  if(t.closest&&t.closest('details.more>summary')){
    setTimeout(function(){const d=document.querySelector('details.more');
      S._moreOpen=!!(d&&d.open)},0);
    return;
  }
  if(t.dataset&&t.dataset.act==='note'){
    S._noteOpen=true;render();
    const b=document.querySelector('.notestrip textarea');if(b)b.focus();
    return;
  }
  if(t.dataset&&t.dataset.act==='noteback'){S._noteOpen=false;render();return}
  if(t.classList&&t.classList.contains('noteadd')){
    const ta=document.querySelector('.notestrip textarea');
    const text=((ta&&ta.value)||S._noteDraft||'').trim();
    if(!text){alert('There is nothing written in the box yet.');return}
    S.notes=S.notes||[];
    S.notes.push({text:text,where:currentWhere()});
    S._noteDraft='';
    persist();render();
    // It travels at once rather than waiting for the next part boundary. A note
    // is often the most perishable thing she writes.
    sendNow(false);
    return;
  }
  if(t.id==='back'){goto2(stepIndex()-1);return}
  if(t.id==='fwd'){goto2(stepIndex()+1);return}
  if(t.dataset&&t.dataset.act==='export'){exportFile();return}
  if(t.dataset&&t.dataset.act==='finalsend'){
    sendNow(true).then(function(ok){
      if(!ok)alert('That could not be sent just now — you may be offline. It will keep '+
        'trying, and "Also keep a copy" downloads a file you can send instead.');
    });
    return;
  }
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
    if(d.detail.split(/\s+/).filter(Boolean).length<8){
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
  if(t.classList&&t.classList.contains('notetext')){S._noteDraft=t.value;return}
  if(t.classList&&t.classList.contains('who')){
    S.reviewer=t.value;clearTimeout(window._pt);window._pt=setTimeout(persist,600);return;
  }
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
  if(!CAN_SAVE)announceNoAutosave();
  const saved=restore();
  if(saved){
    S.path=saved.path||null;
    S.reviewer=saved.reviewer||'';
    S.notes=saved.notes||[];
    const content=Object.keys(saved.answers||{}).length+(saved.raised||[]).length+
                  (saved.notes||[]).length;
    if(content>0){
      S.answers=saved.answers||{};S.raised=saved.raised||[];
      S.act=saved.act||0;S.stop=saved.stop==null?-1:saved.stop;S.mode=saved.mode||'walk';
      // A saved pass from before the paths existed walked all of it. Reading that
      // as "no path chosen" would put her back on the opening page and make her
      // choose before she could reach her own work.
      if(!S.path)S.path='all';
      const el=document.getElementById('resumed');if(el)el.style.display='block';
    }
  }
  // The default length, set for her rather than demanded of her. First entry in
  // PATHS is the shortest, which is the one that makes finishing likeliest; the
  // closing page offers to widen it once she has something to show for the pass.
  if(!S.path)S.path=((DATA.paths||[])[0]||{}).key||null;
  render();sendStatus();
  // A send that failed while she was offline retries when the page next runs and
  // when the connection returns, so an unsent pass repairs itself.
  window.addEventListener('online',function(){if(sendState==='failed')sendNow(false)});
  // The other half of the two-tab problem. Merging on save stops work being
  // erased; this stops the tabs DIVERGING in the meantime, so what she is
  // looking at is what is actually stored rather than a snapshot from before
  // the other tab wrote. Position is left alone — she is not moved.
  window.addEventListener('storage',function(e){
    if(e.key!==KEY)return;
    const merged=mergeSaved(restore());
    S.answers=merged.answers;S.raised=merged.raised;S.notes=merged.notes;
    render();
  });
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='hidden')sendNow(false);
  });
  if(DATA.submit&&(answered()||S.raised.length))sendNow(false);
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

# What she meets first is not the walkthrough. It is what the walkthrough is for.
# The earlier version opened by explaining itself — 52 stops, how the badges work,
# how to save. All true, all secondary. Somebody who has agreed to give an hour to
# a design deserves to see what the design is FOR before being told how the tool
# works. Everything here is drawn from the approved record; none of it is invention.
VISION = {
    "heading": "What success looks like",
    "lede": "Twelve months from the first session, if this works, four things exist "
            "that do not exist today.",
    "outcomes": [
        "Forty health professionals who have each improved something real in their own "
        "service — not attended a programme, produced one — with twelve pieces of "
        "evidence apiece to show for it, and who can now do it again without us and "
        "teach a colleague to do the same.",
        "Nine hospitals qualified against a published standard to host and teach, which "
        "makes the next cohort possible without starting again.",
        "Twelve faculty teaching this here, rather than the country importing it.",
        "Forty improvement projects with baselines and outcomes — a body of evidence on "
        "quality in Nigerian hospitals that nobody currently holds.",
    ],
    "closing": "That is what is being designed. What follows is how, and where it is "
               "still undecided — including what exactly a graduate should be able to "
               "do, which is a question the design has only just written down.",
}

WELCOME = {
    "lede": "You are looking at the design itself, not a summary of it. It is laid out "
            "as a guided walk that stops wherever a decision is still open, or where "
            "what has been built needs testing against what you know.",
    "paragraphs": [
        "You are not being shown a finished thing for approval. Roughly two thirds of "
        "what follows is settled and built; the rest is deliberately unresolved, and "
        "each of those is here because it is better decided with you than presented to "
        "you. Where we have a view, you will see the view and the evidence under it.",
        "A disagreement is as useful to us as an agreement — more useful, if it comes "
        "early. Skipping something is a legitimate answer too: it stays open, and the "
        "design goes on working either way.",
    ],
}

FIELD_LABELS = {
    "what_we_built": "What is built",
    "reopening_note": "Reopening",
}

# How much she takes on. The walk was 52 stops and only one length, which is a
# demanding thing to hand somebody. The stops are not equal: 22 of them can only be
# answered by her, 10 carry a recommendation to argue with, and 20 are settled and
# shown so they can be challenged. Letting her choose the depth at the door turns an
# hour-long obligation into a twenty-minute one she can extend if she wants to.
PATHS = [
    {"key": "essential",
     "label": "Only where I am needed",
     "codes": ["YOUR_KNOWLEDGE", "YOUR_JUDGEMENT", "DESIGN_WITH_US", "HELP_US_SETTLE_IT"],
     "blurb": "The decisions nobody else can make. Things only you or SQHN know, "
              "judgement calls where we have no view, parts not yet designed, and the "
              "one we cannot agree on."},
    {"key": "recommended",
     "label": "Add what we recommend",
     "codes": ["YOUR_KNOWLEDGE", "YOUR_JUDGEMENT", "DESIGN_WITH_US", "HELP_US_SETTLE_IT",
               "ARGUE_WITH_US"],
     "blurb": "The above, plus every place we have put forward a recommendation with "
              "the evidence behind it and would rather have it argued with than accepted."},
    {"key": "all",
     "label": "The whole design",
     "codes": None,
     "blurb": "Everything, including what is already settled and built. Shown because "
              "no decision here is a one-way door."},
]

RAISE_KINDS = [
    ["MISSING_DECISION", "A decision that has to be taken and is not on this list at all."],
    ["MIS_FRAMED", "A question here that is asking the wrong thing."],
    ["WRONG_ASSUMPTION", "Something taken as given that does not hold in practice."],
    ["CONCERN", "Something that worries you and does not fit the other three."],
]

# ---------------------------------------------------------------------------
# The return path
# ---------------------------------------------------------------------------
#
# Without this, getting her answers back means: press Save a copy, find the file
# in Downloads, attach it to an email. Three steps, at the end, when she is
# tired — and the one place where failure costs everything she did. She could
# walk all 52 stops and the programme office would receive nothing.
#
# So a hosted build posts her answers as she goes. Not only at the end: the end
# is precisely the moment a tired person closes a tab. Sending at each part
# boundary means an interrupted pass is still a useful pass.
#
# The endpoint is configured at build time and the page does not care what is
# behind it. Netlify's form handling is what it points at first, because the
# programme needs a host anyway and this comes with it; the mode below is the
# seam that keeps that from becoming a commitment.
#
#   Netlify's requirements, from their documentation (accessed 2 August 2026):
#   the form must exist in the deployed HTML carrying data-netlify="true" and a
#   name; submissions are POSTed URL-encoded, because "Netlify Forms does not
#   support JSON form data at this time"; and form detection must be turned on
#   by hand in the UI before any of it works.
#   https://docs.netlify.com/manage/forms/setup/

SUBMIT_MODES = ("netlify", "json")
DEFAULT_FORM_NAME = "qips-walkthrough-responses"


def submit_config(mode: str | None, url: str | None, form: str | None,
                  reviewer: str | None) -> dict[str, Any] | None:
    """What the page needs to know to send. None means it cannot, and says so."""
    if not mode:
        return None
    if mode not in SUBMIT_MODES:
        raise WalkthroughError(f"unknown submit mode {mode!r}; expected one of {SUBMIT_MODES}")
    if mode == "netlify":
        # Same-origin POST to the site root. Netlify routes it by the form name.
        url = url or "/"
    elif not url:
        raise WalkthroughError("--submit-mode json needs --submit-url")
    return {
        "mode": mode,
        "url": url,
        "form": form or DEFAULT_FORM_NAME,
        "reviewer": reviewer or "",
    }


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
               hosted: bool = False, submit: dict[str, Any] | None = None) -> str:
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
        "vision": VISION,
        "paths": PATHS,
        "raiseKinds": RAISE_KINDS,
        "submit": submit,
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
    # Netlify scans the deployed HTML for forms. A form the page constructs in
    # JavaScript is invisible to that scan, so the form is written out here,
    # hidden, with the fields the send actually uses. Their names must match or
    # the submission arrives with empty columns.
    form = ""
    if submit and submit["mode"] == "netlify":
        # FIELD ORDER IS LOAD-BEARING, and this is not a preference — it is how
        # Netlify decides what a person sees. Their documentation: the submission
        # title is "the first text <input> element that is not hidden and not an
        # email-related field", and the body is "the first <textarea> element in
        # the form, regardless of its name".
        #
        # The first version put the spam honeypot first and the JSON in the only
        # textarea. So every submission was titled with an empty field and its
        # body was a wall of machine-readable text. The inbox is a surface a
        # PERSON reads — the same mistake as letting internal identifiers reach
        # the reviewer, made one layer further out.
        #
        # So: a plain-language summary is the first input, a readable digest of
        # what she actually said is the first textarea, and the machine record is
        # a SECOND textarea, which Netlify ignores for display.
        f = html.escape(submit["form"])
        form = (
            f'<form name="{f}" data-netlify="true" netlify-honeypot="bot-field" hidden>\n'
            f'  <input type="hidden" name="form-name" value="{f}">\n'
            f'  <input name="summary">\n'
            f'  <textarea name="responses"></textarea>\n'
            f'  <input name="reviewer"><input name="progress"><input name="final">\n'
            f'  <input name="bot-field">\n'
            f'  <textarea name="full_record_json"></textarea>\n'
            f'</form>'
        )
    if hosted:
        # Served from an origin: the manifest and the worker are real files, and
        # the browser will offer to install the page as an application.
        head_extra = '<link rel="manifest" href="manifest.webmanifest">'
        register = ("<script>if('serviceWorker' in navigator)"
                    "window.addEventListener('load',function(){"
                    "navigator.serviceWorker.register('sw.js').catch(function(){})});</script>")
    else:
        if submit:
            raise WalkthroughError(
                "a submit endpoint was configured for the single-file build. A page opened "
                "from disk has no origin to post from, so the send would fail every time "
                "and she would be told her answers had not travelled — which would be true. "
                "Configure the endpoint on the hosted build (--pwa) instead."
            )
        form = ""
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
<div class="warnbar nosave" id="nosave" style="display:none">This browser will not let the page
save your progress on its own. Use <b>Save a copy</b> before you close the tab.</div>
<div class="top"><div class="inner">
  <div class="brand">{TITLE}<span>Cohort 1 &middot; SQHN and Partners</span></div>
  <div class="bar"><i id="prog"></i></div>
  <div class="count" id="count">0 of {total}</div>
  <div class="saved" id="saved">saved</div>
  <div class="sendstate" id="sendstate" style="display:none"></div>
</div></div>
{form}
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
    # The compiler records who took each decision under `by`. Carrying the name
    # through here means attribution survives into the minute without her having
    # typed it 52 times.
    who = (payload.get("reviewer") or "").strip()
    responses = []
    for station, body in resolved.items():
        item = dict(body, station=station)
        if who:
            item.setdefault("by", who)
        responses.append(item)
    # Notes travel too. The free-text box is the ONLY route by which something
    # nobody thought to ask about can reach the programme office, and it was
    # reaching the inbox and dying here — visible to whoever read the email,
    # invisible to the record. That is the one loss the box exists to prevent.
    notes = []
    for note in payload.get("notes") or []:
        text = (note.get("text") or "").strip()
        if not text:
            continue
        item = {"text": text, "where": note.get("where") or None}
        if who:
            item["by"] = who
        notes.append(item)
    return {
        "sitting": payload.get("sitting") or SITTING,
        "reviewer": who or None,
        "responses": responses,
        "raised": payload.get("raised") or [],
        "notes": notes,
    }


def write_pwa(directory: Path, acts: list[dict[str, Any]], stations: list[dict[str, Any]],
              commit: str, submit: dict[str, Any] | None = None) -> list[Path]:
    """Write the hosted form: the same page, plus what makes it installable.

    Four files, all static, no build step and no server code — it can go on any
    static host, including whatever the programme ends up using. The single-file
    build stays the default and stays the thing that is sent by email; this is
    what turns it into something with an icon on her dock.
    """
    directory.mkdir(parents=True, exist_ok=True)
    page = build_html(acts, stations, commit, hosted=True, submit=submit)
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

def unterminated_string_literals(source: str) -> list[str]:
    """Find a string literal broken across a newline. It is not legal JavaScript.

    This exists because the whole page silently died once. The JavaScript is held
    in a Python string, so a `\\n` written with one backslash instead of two
    becomes a REAL newline inside a JS quote — and JavaScript will not have that.
    The page rendered its shell, the script never ran, and every check in this
    file still passed, because none of them had ever looked at the JavaScript as
    JavaScript. It took a browser to find it.

    A scanner rather than a dependency: the check has to run wherever the gates
    run, including machines with no Node installed.
    """
    problems: list[str] = []
    quote: str | None = None
    escaped = False
    line = 1
    started = 1
    index = 0
    while index < len(source):
        ch = source[index]
        if ch == "\n":
            if quote in ("'", '"'):
                problems.append(
                    f"a {quote} string opened on line {started} is still open at the end of "
                    f"the line. JavaScript does not allow a newline inside one, so the whole "
                    f"script fails to parse and nothing on the page runs."
                )
                quote = None
            line += 1
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
        elif ch in "'\"`":
            quote, started = ch, line
        elif ch == "/" and source[index:index + 2] == "//":
            index = source.find("\n", index)
            if index < 0:
                break
            continue
        elif ch == "/" and source[index:index + 2] == "/*":
            end = source.find("*/", index + 2)
            if end < 0:
                break
            line += source.count("\n", index, end)
            index = end + 2
            continue
        index += 1
    return problems


def self_test() -> int:
    failures: list[str] = []

    # This file is mostly not Python. The style sheet and the script are held in
    # Python strings, and the translation between the two languages is where the
    # damage happens: a backslash Python does not recognise is kept with a
    # warning, one Python DOES recognise is silently transformed, and either way
    # the browser gets something other than what is written here.
    #
    # The script block is a raw string so there is no translation at all. This
    # check is what keeps it that way, and it fires on the warning Python was
    # already printing on every run and nobody was reading.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    for warning in caught:
        failures.append(
            f"line {warning.lineno}: {warning.message}. In a block of JavaScript this is "
            f"never harmless — it means the browser receives different characters from the "
            f"ones written here. Use a raw string, or double the backslash deliberately."
        )

    # Before anything else: the page's script must be parseable. Everything below
    # tests what the page CONTAINS; this tests that it can run at all.
    for problem in unterminated_string_literals(JS):
        failures.append(f"the page's script is not valid JavaScript: {problem}")
    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
            handle.write(JS)
            probe = handle.name
        try:
            checked = subprocess.run([node, "--check", probe], capture_output=True, text=True)
            if checked.returncode:
                first = (checked.stderr or "").strip().split("\n")
                failures.append("node rejects the page's script: " + " / ".join(first[:4]))
        finally:
            Path(probe).unlink(missing_ok=True)
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

    # Storage is not always available: private windows, "block all cookies", and
    # some browsers' handling of a page opened straight from disk all refuse it.
    # The first version caught the exception and carried on, which is the worst
    # possible behaviour — the opening page promised that answers save themselves
    # and then an hour of work vanished on reload with nothing visibly wrong.
    # A page that cannot keep the promise must stop making it, visibly.
    for marker, missing in [
        ("storageWorks", "the page never checks whether it can actually save"),
        ("CAN_SAVE", "nothing carries the answer to that check into what the page says"),
        ("id=\"nosave\"", "there is nowhere to tell her autosave is not working"),
    ]:
        if marker not in html_out:
            failures.append(f"silent data loss: {missing}")
    if re.search(r"catch\(e\)\{\}", JS):
        failures.append(
            "a swallowed exception remains in the page. Every failure here is one the "
            "reviewer needs told about, because she cannot see that it happened."
        )

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

    # --- the return path ---------------------------------------------------
    # Without an endpoint the page must still tell her how to get her answers
    # back, or she finishes and has nowhere to put them.
    if "Save a copy" not in html_out:
        failures.append("with no endpoint configured, the page offers no way to return answers")

    cfg = submit_config("netlify", None, None, "A Reviewer")
    hosted_submit = build_html(acts, stations, "self-test", hosted=True, submit=cfg)

    form = re.search(r"<form [^>]*data-netlify[^>]*>.*?</form>", hosted_submit, re.S)
    if not form:
        failures.append(
            "the hosted build carries no static form. Netlify scans the deployed HTML, so a "
            "form built in JavaScript is invisible to it and every submission is dropped."
        )
    else:
        if f'name="{cfg["form"]}"' not in form.group(0):
            failures.append("the static form's name does not match the name the page posts under")
        # The failure this catches is quiet and total: a submission arrives, and
        # every column is empty, because the field names did not agree.
        declared = set(re.findall(r'<(?:input|textarea) name="([\w-]+)"', form.group(0)))
        declared |= set(re.findall(r'<input type="hidden" name="([\w-]+)"', form.group(0)))
        sent = set(re.findall(r"f\.append\('([\w-]+)'", JS))
        missing = sent - declared
        if missing:
            failures.append(
                f"the page posts field(s) the form does not declare: {sorted(missing)}. "
                f"The submission would arrive with those columns empty."
            )

        # ORDER, not just names. Netlify builds what a person sees from the first
        # non-hidden text input (the title) and the first textarea (the body).
        # The first version put the spam honeypot first and the machine record in
        # the only textarea, so every submission was titled with an empty field
        # and its body was a wall of JSON. Names all agreed; the inbox was still
        # unreadable. Found by a human looking at it, which is the argument for
        # looking at it.
        body_html = form.group(0)
        visible = re.findall(r'<input (?!type="hidden")name="([\w-]+)"', body_html)
        areas = re.findall(r'<textarea name="([\w-]+)"', body_html)
        if not visible or visible[0] != "summary":
            failures.append(
                f"the first plain input is {visible[0] if visible else 'missing'!r}, so that is "
                f"what titles every submission. It must be the human summary."
            )
        if not areas or areas[0] != "responses":
            failures.append(
                f"the first textarea is {areas[0] if areas else 'missing'!r}, so that is what "
                f"Netlify shows as the body of every submission. It must be the readable "
                f"digest, never the machine record."
            )
        if "full_record_json" in areas[:1]:
            failures.append("the machine record is the first textarea; a person would read JSON")

    for marker, missing in [
        ("sendNow", "nothing sends her answers back"),
        ("visibilitychange", "a pass abandoned mid-part is never sent"),
        ("addEventListener('online'", "a send that failed offline never retries"),
        ("id=\"sendstate\"", "she cannot see whether her answers travelled"),
    ]:
        if marker not in hosted_submit:
            failures.append(f"return path: {missing}")

    # Configuring an endpoint on the single-file build must be refused, not
    # accepted and then quietly broken: a page opened from disk has no origin to
    # post from, so every send would fail and she would be told so, correctly and
    # uselessly, for the whole pass.
    try:
        build_html(acts, stations, "self-test", hosted=False, submit=cfg)
    except WalkthroughError:
        pass
    else:
        failures.append("a submit endpoint was accepted on the single-file build, where it cannot work")

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
            # Installing the application must not sever the return path. A worker
            # that handled every request would answer the POST from its cache, the
            # send would appear to succeed, and her answers would go nowhere — the
            # worst available failure, because it is silent. The worker must
            # decline anything that is not a GET.
            fetch_handler = cached.split("'fetch'", 1)[-1]
            if "method!=='GET'" not in fetch_handler.replace(" ", ""):
                failures.append(
                    "the worker intercepts more than GETs, so an installed application "
                    "could answer her submission from cache and lose it silently"
                )

    # --- the opening page --------------------------------------------------
    # Order is the whole argument here. Somebody opening a link asks what this is
    # FOR before asking what it is, and asks how long it will take before
    # agreeing to start. A page that leads with mechanics gets closed.
    welcome_src = JS.split("function screenWelcome(", 1)[-1].split("\nfunction ", 1)[0]
    order = [("DATA.vision", "what success looks like"),
             ("DATA.welcome.lede", "what this is"),
             ("DATA.paths", "how long it is"),
             ('details class="more"', "everything else, behind a disclosure")]
    found = [(welcome_src.find(needle), label) for needle, label in order]
    if any(i < 0 for i, _ in found):
        failures.append(
            "the opening page is missing one of: "
            + ", ".join(label for i, label in found if i < 0)
        )
    elif [i for i, _ in found] != sorted(i for i, _ in found):
        failures.append(
            "the opening page states its mechanics before its purpose: got "
            + " then ".join(label for _, label in sorted(found))
        )
    # The legend explains six question types she has not met yet. In front of the
    # Begin button it was a third of the opening page and 1.5 phone screens of
    # scrolling between her and starting. It belongs behind the disclosure.
    if 'details class="more"' in welcome_src:
        before, _after = welcome_src.split('details class="more"', 1)
        if 'class="legend"' in before:
            failures.append(
                "the legend sits in front of the Begin button again; it is reference for "
                "badges she meets in context and pushes the start off the screen"
            )

    # --- starting must not require a decision ------------------------------
    # The paths exist to remove a demand. Gating Begin on choosing one puts the
    # demand back: she cannot start until she has ruled on something she has no
    # basis to rule on yet. A default she can change is an offer.
    if re.search(r"f\.disabled\s*=[^;]*S\.path", JS):
        failures.append(
            "Begin is disabled until she picks a length; that is the demand the lengths "
            "were introduced to remove"
        )
    if "S.path=((DATA.paths||[])[0]||{}).key" not in JS.replace(" ", ""):
        failures.append(
            "no length is chosen for her at startup, so the walk cannot begin until she "
            "decides something she has no basis to decide yet"
        )
    # The default is what most reviewers will actually walk, so it has to be the
    # one they can finish. The nesting check below proves the first entry is the
    # shortest; this proves it is bounded at all.
    if PATHS[0]["codes"] is None:
        failures.append(
            "the default length is the whole design, which is the demand this was "
            "meant to remove"
        )

    # --- how much she is asked to take on ----------------------------------
    # Handing a busy reviewer 52 stops with no way to scale it is a demand, and a
    # demand is the likeliest reason this never gets read. The paths must nest —
    # a wider one may only ADD — or "widen it, nothing is lost" becomes untrue.
    by_code: dict[str, int] = {}
    for act in payload["acts"] if payload else []:
        for stop in act["stops"]:
            code = (stop.get("needs") or {}).get("code")
            if code:
                by_code[code] = by_code.get(code, 0) + 1
    sets = []
    for path in PATHS:
        codes = path["codes"]
        size = sum(by_code.values()) if codes is None else sum(by_code.get(c, 0) for c in codes)
        sets.append((path["key"], set(by_code) if codes is None else set(codes), size))
        if size == 0:
            failures.append(f"path {path['key']!r} would offer her nothing to do")
        for unknown in (codes or []):
            if unknown not in by_code:
                failures.append(
                    f"path {path['key']!r} names {unknown!r}, which no stop carries; "
                    "its count would be a promise the walk cannot keep"
                )
    for (ka, sa, na), (kb, sb, nb) in zip(sets, sets[1:]):
        if not sa <= sb:
            failures.append(
                f"path {ka!r} is not contained in {kb!r}; widening would drop stops she "
                "had already been shown"
            )
        if not na < nb:
            failures.append(f"path {ka!r} is not shorter than {kb!r}, so the choice is empty")
    if sets and sets[-1][2] != len(stations):
        failures.append(
            f"the widest path shows {sets[-1][2]} of {len(stations)} stops; it is offered "
            "as the whole design"
        )

    # --- what she says where nothing asked ---------------------------------
    # The free text is the only input on the page not attached to a question we
    # thought to ask, which makes it the only route by which something we did not
    # anticipate can reach us. Every place her work is stored, sent or written
    # out has to carry it, or it becomes the one thing she said that we lose.
    for where, marker, missing in [
        ("the record that is sent", "function payload(", "notes:S.notes"),
        ("the downloaded copy", "function exportFile(", "notes:S.notes"),
        ("what is saved in her browser", "function persist(", "notes:S.notes"),
        ("what is read back", "function restore(", None),
        ("the human digest", "function readable(", "S.notes"),
    ]:
        if marker not in JS:
            failures.append(f"{where}: {marker} has gone")
            continue
        if missing and missing not in JS.split(marker, 1)[1].split("\nfunction ", 1)[0]:
            failures.append(
                f"her free text never reaches {where}; she would write it and we would "
                "never see it"
            )
    if "S.mode!=='doc')body+=noteStrip()" not in JS.replace(" ", ""):
        failures.append(
            "the free-text box is not appended to every screen of the walk, so what she "
            "can say depends on where she happens to be"
        )
    # Nothing here renders CSS, so a layout defect is invisible to every other
    # check in this file. This one is pinned by name because it already shipped
    # once: written as a descendant selector it also caught the standing note
    # nested inside each row and stacked it one word per line.
    if re.search(r"^\.legend\s+div\s*\{", CSS, re.M):
        failures.append(
            "the legend styles every nested div, not just its own rows; the standing "
            "note inside a row becomes a second grid and breaks one word per line"
        )
    if "white-space:normal" not in CSS.split(".legend>div>.needs{", 1)[-1].split("}", 1)[0]:
        failures.append(
            "the legend badge cannot wrap, so a long label runs over the sentence beside it"
        )
    # --- the page must not claim a delivery it cannot verify ---------------
    # Netlify answers a processed form with a redirect and an ignored POST with
    # the static file at that path. Both are 200. Treating 2xx as delivery meant
    # the likeliest misconfiguration in the whole deployment — form detection
    # left off, which the runbook warns about at length — displayed as "sent to
    # the programme office" at every part boundary while nothing arrived.
    if submit_cfg := submit_config("netlify", None, DEFAULT_FORM_NAME, None):
        hosted_netlify = build_html(acts, stations, "self-test", hosted=True, submit=submit_cfg)
        # Matched as an ASSIGNMENT, not as an identifier. The first version of
        # this gate asked whether "r.redirected" appeared anywhere in the page —
        # and it does, in the comment three lines above the code. Replacing the
        # real check with `sendConfirmed=true` left the gate green. A gate that
        # can be satisfied by prose is not a gate.
        if not re.search(r"sendConfirmed\s*=\s*!!\s*r\.redirected", hosted_netlify):
            failures.append(
                "the send treats any 2xx as delivered. A POST Netlify never processed answers "
                "200 with the page itself, so an unconfigured form would read as sent and she "
                "would finish believing an hour of work had travelled"
            )
        # Likewise checked by the words she would actually read, not by whether
        # the variable is mentioned somewhere in the function.
        status_fn = JS.split("function sendStatus(", 1)[-1].split("\nfunction ", 1)[0]
        if "not yet acknowledged" not in status_fn:
            failures.append(
                "the status line reads the same whether or not the send was acknowledged"
            )
        if not re.search(r"sendConfirmed\s*\?", status_fn):
            failures.append("the status line does not branch on whether the send was acknowledged")
        finish_fn = JS.split("function screenFinish(", 1)[-1].split("\nfunction ", 1)[0]
        # Read the BRANCH, not the function. "keep a copy" appears on this screen
        # either way — it is a button label — so checking the whole function
        # would pass with the branch gutted. Everything asserted below has to
        # come from inside the unacknowledged case itself.
        if "!sendConfirmed){" not in finish_fn:
            failures.append(
                "the closing screen says the same thing whether or not delivery was "
                "acknowledged — the last moment the doubt is cheap to settle"
            )
        else:
            branch = finish_fn.split("!sendConfirmed){", 1)[1].split("\n  }", 1)[0]
            if "did not acknowledge" not in branch:
                failures.append("the closing screen does not say what is actually unknown")
            if "keep a copy" not in branch.lower():
                failures.append(
                    "the closing screen raises a doubt without naming the thirty-second fix; "
                    "a warning with no remedy is just anxiety"
                )

    # --- reachable by someone not using a mouse -----------------------------
    # None of this was tested until a stress pass went looking. A heading that
    # skips a level is how a screen-reader user loses the shape of the page,
    # and a control with no accessible name is read out as "button".
    if re.search(r"<h1[^>]*>.*?<h3", JS.replace("\\n", ""), re.S) and "sec" not in CSS:
        failures.append("section headings jump from h1 to h3, so the page has no level 2")
    if 'lang="en"' not in html_out:
        failures.append("reachability: the document does not declare its language")
    # Checked on the BUTTON's own markup. Asking whether the phrase "Speak
    # instead of typing" appears anywhere passed with the attribute deleted,
    # because the same phrase is also assigned at runtime further up the file.
    # An icon-only control with no name is announced as "button".
    box_fn = JS.split("function box(", 1)[-1].split("\nfunction ", 1)[0]
    if "data-mic" not in box_fn:
        failures.append("reachability: the dictation control has moved; this check is stale")
    elif "aria-label" not in box_fn.split("data-mic", 1)[1].split(">'+MIC", 1)[0]:
        failures.append(
            "reachability: the microphone is an icon with no accessible name, so a screen "
            "reader announces it as 'button' and nothing else"
        )
    # The install control is hidden until the browser offers it. When it appears
    # it was auto-placed onto a third row of the mobile navigation that the page
    # padding did not allow for, hiding the end of the page behind it.
    if "#install{grid-area" not in CSS.replace(" ", ""):
        failures.append(
            "the install control has no place in the mobile navigation, so it pushes a row "
            "the page does not make room for"
        )
    mobile_pad = re.search(r"main\{padding:24px 15px (\d+)px\}", CSS)
    if not mobile_pad or int(mobile_pad.group(1)) < 180:
        failures.append(
            "the mobile page does not leave room for the navigation at its tallest; the last "
            "thing on the page sits behind it"
        )

    # --- two tabs -----------------------------------------------------------
    # Storage is shared per browser and each tab holds its own copy in memory, so
    # a save that writes memory out wholesale erases whatever the other tab did.
    # Measured before the fix: three answers in one tab, one in a second, one
    # left. Silent, and she opens an emailed link twice without thinking.
    persist_fn = JS.split("function persist(", 1)[-1].split("\nfunction ", 1)[0]
    if "mergeSaved(restore())" not in persist_fn.replace(" ", ""):
        failures.append(
            "a save overwrites what is stored instead of merging with it; a second tab "
            "erases the first tab's work with no error and no warning"
        )
    if "function mergeSaved(" not in JS:
        failures.append("nothing merges a save with what another tab already wrote")
    else:
        # Checked as a READ FROM WHAT IS STORED — prev.<field> — not as the bare
        # word appearing somewhere in the function. Reading `prev` is the entire
        # difference between a merge and an overwrite, and a gate that accepts
        # the word "notes" is satisfied by a local variable of that name.
        merge_fn = JS.split("function mergeSaved(", 1)[1].split("\nfunction ", 1)[0]
        for field, why in [
            ("answers", "answers from the other tab would be dropped"),
            ("raised", "a raised item from the other tab would be dropped"),
            ("notes", "a note from the other tab would be dropped"),
        ]:
            if f"prev.{field}" not in merge_fn:
                failures.append(f"the merge never reads the stored {field}; {why}")
    if "addEventListener('storage'" not in JS.replace('"', "'"):
        failures.append(
            "a tab never learns that another tab wrote, so the two drift apart and what she "
            "sees stops matching what is saved"
        )

    # The last boundary, and the one her free text was actually dying at. It
    # reached the inbox — a human reading the email saw it — and then to_capture
    # dropped it, so it never entered the compiled record at all. Proved by
    # round-tripping a real note rather than by reading the code.
    probe_stop = stations[0]["id"] if stations else None
    if probe_stop:
        probe = {
            "sitting": SITTING, "generated_from": "self-test",
            "journey_fingerprint": journey_fingerprint(acts),
            "reviewer": "Self Test",
            "responses": [{"station": stop_key(0, 0), "response": "ACCEPT", "reason": ""}],
            "raised": [],
            "notes": [{"text": "a thought no question asked for", "where": "part 1"}],
        }
        try:
            carried = to_capture(probe, acts).get("notes") or []
        except Exception as exc:  # noqa: BLE001
            carried = []
            failures.append(f"the conversion refused a valid record carrying a note: {exc}")
        if not carried:
            failures.append(
                "her free text does not survive into the record the compiler reads. It would "
                "reach the inbox and stop there — the one loss the free-text box exists to "
                "prevent"
            )
        elif carried[0].get("text") != "a thought no question asked for":
            failures.append("a note is altered on its way into the record")
        elif not carried[0].get("where"):
            failures.append("a note reaches the record without where she was when she wrote it")

    if "where:currentWhere()" not in JS.replace(" ", ""):
        failures.append(
            "a note is stored without where she was; the same sentence means different "
            "things on different parts and she should not have to say which"
        )


    # A contested recommendation must never reach her wearing a confident face.
    # This is the one failure in this file that would actively mislead rather
    # than merely confuse: she would calibrate how hard to push against a
    # confidence the programme office does not have.
    if payload:
        contested = [stop for act in payload["acts"] for stop in act["stops"]
                     if (stop.get("recommendation") or {}).get("under_review")]
        for stop in contested:
            rec = stop["recommendation"]
            if (stop.get("needs") or {}).get("code") != "HELP_US_SETTLE_IT":
                failures.append(
                    "a stop whose recommendation is under review still says 'we recommend "
                    "this — argue with it'. We do not recommend it; we do not agree."
                )
            if rec.get("status") != "UNDER_REVIEW_NOT_A_RECOMMENDATION":
                failures.append("a contested recommendation still reports itself as standing")
            positions = (rec.get("under_review") or {}).get("the_competing_positions") or []
            if len(positions) < 2:
                failures.append(
                    "a recommendation is marked under review but fewer than two positions are "
                    "shown. 'Under review' with one option is just a recommendation hedged."
                )
            for position in positions:
                if not position.get("case_against"):
                    failures.append(
                        f"position {position.get('name')!r} is shown with no case against it. "
                        f"A choice presented without its cost is not a choice."
                    )
        if contested and "contested" not in html_out:
            failures.append("nothing in the page renders the contested block")

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
    parser.add_argument("--submit-mode", choices=SUBMIT_MODES,
                        help="how the hosted page returns her answers")
    parser.add_argument("--submit-url", help="where to post; defaults to the site root for netlify")
    parser.add_argument("--submit-form", help=f"form name; defaults to {DEFAULT_FORM_NAME}")
    parser.add_argument("--reviewer", help="name the responses arrive under, if not asked on the page")
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
        # Notes are counted out loud. They were being dropped here silently, and
        # a count that omits them is how nobody noticed: the command reported
        # success and the operator had no way to tell what had not come through.
        print(f"read {len(capture['responses'])} response(s), "
              f"{len(capture['raised'])} raised item(s) and "
              f"{len(capture['notes'])} note(s) -> {args.capture_out}")
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
        submit = submit_config(args.submit_mode, args.submit_url, args.submit_form, args.reviewer)
        for path in write_pwa(Path(args.pwa), acts, stations, args.commit, submit):
            print(f"wrote {path}")
        print("\nServe that directory over http(s) and the browser will offer to install it.\n"
              "Opened straight from disk it still works, offline — it just cannot install,\n"
              "because installing needs a service worker and a worker needs an origin.")
        if submit and submit["mode"] == "netlify":
            print(f"\nResponses post to '{submit['url']}' as form '{submit['form']}'.\n"
                  f"Netlify will not accept them until form detection is switched on by hand:\n"
                  f"  Netlify UI -> Forms -> Enable form detection, then redeploy.\n"
                  f"Until that is done every send fails, and the page says so rather than\n"
                  f"pretending otherwise.")
        elif not submit:
            print("\nNo submit endpoint configured: she downloads a file and sends it herself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
