# BATON — QIPS Programme Office · cross-agent handoff

| | |
|---|---|
| Project | Designing and governing the SQHN Professional Programme in Healthcare Quality and Patient Safety — cohort 1, Nigeria-anchored |
| Handoff issued | 6 August 2026, by a Claude session (Cowork) |
| Baton state | v1 — design substantially complete, curriculum content largely unbuilt |
| Owner of record | The programme director (@ruavira). **Every approval flows through him.** No agent decides. |
| Receiving agent | Any — Codex, ChatGPT, Claude. Read this whole file before acting. |

---

## 1 · Mission

A twelve-month hybrid professional programme in healthcare quality and patient safety, convened by
SQHN and Partners, for working health professionals in Nigeria and comparable markets. Cohort 1 is
scheduled January–December 2027 (a start-date change to April 2027 is under consideration — see §6).
Participants do not attend and consume; each produces twelve artefacts carrying one real improvement
in their own service, plus a forty-hour observership and a capstone.

This repository is the programme's operating system: seventeen workstreams, an approved record
(`canon/`), an open-questions register, a decision-capture engine, and a generated design
walkthrough that a committee member walks in a browser to record verdicts.

Deeper context: `README.md`, `docs/operating-model.md`, `QIPS-Programme-Office-Architecture.md`.

## 2 · Ground truth, in precedence order

1. **This repository.** `canon/` is the only thing that is TRUE. Everything else is proposal,
   research or draft. Where a document and canon disagree, canon wins.
2. **CCC minutes** (`ccc/minutes/`) — the human decisions that wrote canon. A canon entry without a
   minute is a defect.
3. **The Claude Project "Nigeria QIPS Professional Program"** — a mirror, not a source. Holds
   research dossiers, council verdicts and status notes in readable form. Useful to a Claude
   session; not required by any other agent. Nothing there overrides the repository.
4. **Live systems** — the design walkthrough deployed at `https://qips-walkthrough.netlify.app`
   (Netlify site id is in `~/qips-site/.netlify/state.json` on the owner's machine, not here), and
   the GitHub repository `ruavira/qips-programme-office` (public).
5. **Not in this repository, by decision:** participant personal data, partner source documents,
   any credential. Ask the owner.

## 3 · Repo map

`canon/` — the approved record: `facts.yaml` (29 facts), `open-questions.yaml` (14 questions),
`glossary.md` (controlled vocabulary, enforced), `dependencies.yaml`. **Write only via a CCC
verdict.** `CODEOWNERS` routes it to the owner.

`ccc/` — the committee: minutes, generated agenda, generated control room. `agenda.md` and
`control-room.html` are GENERATED; edit the generators, not the output.

`engine/` — the machinery. `decision_interview.py` turns canon into 56 review stations;
`walkthrough.py` renders those into a self-contained browser page and reads her answers back;
`curriculum.py` validates the spine and enforces the controlled vocabulary; `admissions.py`,
`parameters.py`, `decision_capture.py`, `validate_ikr_pos.py` each own a check. `engine/schemas/`
holds the data those read — recommendations, journey, spine, rubric, reviewer language.

`workstreams/W01…W17/` — per-workstream working documents. Drafts live here, never in canon.

`docs/`, `governance/`, `contracts/`, `documents/` — operating model, IKR-POS profile, agreements,
reference material.

## 4 · Access checklist — how to obtain, never the secrets

| Need | For | How to get it |
|---|---|---|
| GitHub write access to `ruavira/qips-programme-office` | pushing proposal branches | Ask the owner. Public repo, so reading needs nothing. |
| Netlify account access | redeploying the walkthrough | Owner's account; `npx netlify-cli` on his machine already carries the login. Do not request a token. |
| SQHN standards, minutes, partner agreements | evidence work | Owner provides. Some are not public. |
| Anything else | — | Ask. **No agent should ever hold a credential for this project.** |

**If you are a Claude Cowork session:** the owner's folders are granted per session and do not
carry over. Call `get_device_info` before you build anything, and request `~/qips-programme-office`
and `~/qips-site` in a single dialog. You can then read his repository state and the built site
directly instead of asking him to run commands. This is not a convenience — a previous session lost
a working day to round trips it could have avoided with one call.

**A write credential must never transit a chat.** This repository's CI greps for token patterns and
fails the build on a hit. The established delivery pattern is a proved patch bundle the owner runs
himself — see §8.

## 5 · STATE — append-log, newest first

**8 August 2026 (Claude/Cowork → next agent):**

- **DONE — baton received and verified before any work.** All eleven §8 checks green at
  `64890a1` on the clone, the GitHub remote and the owner's own disk (read directly over the
  device bridge, per §4 — both folders granted in one dialog). The three surfaces agreed
  byte-for-byte on branch and commit. One informational note: `decision_interview.py --check`
  reports ST-F017 in the research queue needing a recommendation; not a failure, recorded here
  so it is not rediscovered.
- **DONE — the IN-FLIGHT item: months 3–12 defined at spine level.** All ten outlined months
  brought to the standard months 1 and 2 already meet — performance outcome, why the month sits
  where it does, evidence the participant submits, connection to the capstone — in
  `workstreams/W02/working/W02-months-3-12-spine-definitions-2026-08-08.md`. Grounded in
  F003/F004/F006/F010/F019, the objectives document's twelve draft outcomes, and the existing
  employer evidence; no new external figures introduced. Five new unresolved assumptions
  recorded (UA6–UA10). The document carries merge-ready YAML under a proposed third detail
  level `spine`, plus the two-line validator amendment required on adoption, so a committee yes
  is a minute plus a mechanical merge. **The spine YAML itself is untouched** — Item 1
  authorised months 1–2 full and 3–12 outline, `engine/curriculum.py` enforces exactly that,
  and the check was honoured, not worked around. **This is NOT the teaching content**; Q014
  stays open and now has a defined target to author against.
- **IN-FLIGHT — the definitions document is with the owner.** He reads it and either routes it
  to the CCC (Lane 3, or an agenda item at the next sitting) or asks for revision. On adoption:
  the mechanical merge, the validator amendment, and the new check proved to fire by deleting
  one month's performance outcome and watching it go red.
- **NOT STARTED:** unchanged from the blocks below, with one correction of scale: "author
  months 3–12" now means the teaching content only (ten eLearning releases, learning maps,
  live-session plans, artefact briefs, draft rubrics, accessibility equivalents), the spine
  level being done. The merge item now reads 24 commits, not 20.

**6 August 2026, later (Claude/Cowork → next agent):**

- **DONE — four decisions taken by the owner in a structured interview**, after he said plainly he
  was struggling with the number of open decisions and the conflicting views. Recorded in the
  Claude Project as `QIPS-Director-Decisions-2026-08-06.md` and reflected in §6 below.
  **(1)** The start-date verdict is DEFERRED and now formally blocked on one answer from SQHN
  finance — a drafted question is with the owner. **(2)** Four standing defaults ACCEPTED
  (competency claim, coverage map, framework parked, patient-safety gap ships visible); tuition
  PULLED BACK for a deliberate decision. **(3)** Next build is months 3–12 of the curriculum.
  **(4)** The link to Dr. Oyewumi is HELD until the curriculum question is answered — which
  removes the journey-fingerprint constraint, since no review pass has begun.
- **DONE — the repository now announces its own baton.** `README.md`, `AGENTS.md` (item 0, which is
  what Codex reads by convention) and `CLAUDE.md` all point at this file. Previously none of them
  did, so an agent landing on the repository would not have found it. `CLAUDE.md` also carries the
  device-bridge lesson: inventory your channels before building.
- **IN-FLIGHT — months 3 to 12, spine level first.** Draft the artefact definition for each of the
  ten outlined months to the standard months 1 and 2 already meet: performance outcome, why it sits
  where it does, the evidence the participant submits, and how it connects to the capstone. This
  unblocks six workstreams and is days of work. **It is NOT the teaching content**, which is the
  body of work Q014 is really about — do not report the two as one thing.
- **NOT STARTED:** unchanged from the block below.

**6 August 2026 (Claude/Cowork → next agent):**

- **DONE — the design walkthrough is built, deployed and current.** 56 stops across 9 parts,
  offered at three lengths (23 / 35 / 56) with the shortest pre-selected so nothing is demanded
  before the reviewer can start. Opens with what success looks like at twelve months. Saves as she
  goes, merges across browser tabs, carries a free-text box on every screen, posts answers back
  part by part, and reports honestly when a send was not acknowledged. *Verified:* repository tree
  `4a5b9ec1…`, built artefact `qips-walkthrough-d618ab03e0a5` reproduced independently from the
  same tree and matching byte-for-byte on the owner's disk.
- **DONE — an adversarial stress pass found eight defects, six of them silent.** Free text never
  reached the compiled record; any HTTP 2xx read as "delivered" even when Netlify had ignored the
  POST; two browser tabs erased each other's work; a pasted URL blew the layout 52,000px wide; the
  command-line wiring had no test; plus a heading-level skip, a mobile navigation overflow and an
  unnamed microphone control. All fixed, each with a gate proved to fire on the defect by
  restoring it.
- **DONE — the competency gap closed as far as it can be without the committee.** The design had
  never stated what a graduate can do; canon contained no competency facts and no stop asked.
  Research established three things: no competency framework for healthcare quality professionals
  has been authored anywhere in Africa (two independent 2026 peer-reviewed reviews); employers do
  not ask for a quality credential (one of eighteen adverts, four years old, anonymous employer);
  and the most common duty asked of a quality professional is *teaching other staff*. Q011, Q012
  and Q013 added; a drafted claim and coverage map now reach the reviewer as recommendations to
  argue with. Full evidence in `workstreams/W02/working/`.
- **DONE — Q014 recorded: ten of the twelve months do not exist.** See §6 item 5.
- **IN-FLIGHT — the next mechanical step, runnable without any decision:**
  ```
  cd ~/qips-programme-office && python3 engine/walkthrough.py --pwa ~/qips-site \
      --submit-mode netlify --reviewer "Dr Oyewumi" --commit "$(git rev-parse --short HEAD)"
  cd ~/qips-site && npx netlify-cli deploy --dir . --prod
  ```
  Rebuilds and republishes the walkthrough from whatever the branch currently holds. Safe to run at
  any time; idempotent in effect.
- **NOT STARTED, in order:**
  1. Author months 3–12 of the curriculum (the largest remaining work — §6 item 5).
  2. Write the one eLearning release covering reading a service against a published standard.
  3. Merge `proposal/decision-interview` (20 commits) to `main` once the owner has reviewed.
  4. Resolve the patient-safety gap: taught but not demonstrated, in a programme carrying patient
     safety in its name.

## 6 · Human action register — the owner's, do not silently absorb

**Sorted by whether it genuinely needs a human decision.** This ordering was produced deliberately:
the previous agent generated more open decisions than the owner could close, and separating them is
part of the handoff.

### A · Only he or SQHN can decide, and things are blocked until he does

1. **The start date — DEFERRED 6 Aug, and now blocked on one answer.** The owner will not take the
   verdict until SQHN finance confirms whether the USD 15,210 is an incremental cheque or salaried
   staff time already on payroll. Incremental cash makes the shortfall roughly USD 17,500 and cohort
   1 needs a named funder; salaried time makes the real hole about USD 2,200 and SQHN can carry it.
   A drafted question is with the owner, targeting a reply by 20 August so it lands with the
   indemnity figures on the 21st. **Do not re-open the calendar argument until that answer exists.**
   The underlying recommendation: a six-advisor council recommended Option B — April 2027, redesigned to ten
   coaching groups and eighty seats — because cohort 1 **cannot break even inside a ceiling of 64
   seats at any price**. Best case needs 70; eighty seats is the first configuration that returns
   (+2,340). Fixed cost is USD 40,780. Accept, or overturn with a reason. *Blocks: the whole
   calendar, marketing, admissions.*
2. **Whether SQHN amends QI 5.1** from *"may appoint"* to a scored criterion with a qualification
   floor. Two independent pieces of work have arrived at this as the highest-value action
   available: it costs nothing, is entirely within SQHN's gift, and would create the employer
   demand the programme is otherwise trying to manufacture. *Blocks: the institutional sale.*
3. **Ask SQHN finance, in writing,** whether the USD 15,210 is incremental cash or salaried staff
   time. The council named this the one thing to do first. *Blocks: the financial model's meaning.*
4. **The programme's name** (Q010, due 31 Aug) and **the certificate title and awarding authority**
   (Q002, due 31 Aug). Both need SQHN, not analysis.
14. *(added 8 Aug — numbered out of sequence so older references to items 5–13 stay true)*
   **Route the months 3–12 spine definitions to the committee.** The draft is in
   `workstreams/W02/working/W02-months-3-12-spine-definitions-2026-08-08.md`, written to be
   argued with. Nothing enters the spine without a minute; until then the ten months remain
   outline in every published surface. *Blocks: the mechanical merge, and full value of the
   unblocking this gives W05, W06, W09, W10, W11 and W14.*

### B · Defaults — FOUR ACCEPTED 6 Aug, ONE PULLED BACK. Do not re-litigate the accepted four.

5. **Tuition — PULLED BACK 6 Aug for a deliberate decision.** The committee ratified 450–600
   working 500, with reasons minuted; an agent reopened it, not new evidence. The owner declined to
   simply accept the default because it carries real money. It does not revert to "contested by
   default" — it becomes a decision to be taken with the comparator corridor and the three competing
   positions in front of whoever takes it. Until then the page shows it as under review, which is
   the honest presentation either way.
6. **ACCEPTED.** The competency claim (Q011) and the coverage map (Q012). Both are drafted, evidence-backed
   and reach the reviewer as recommendations. **Default: let them stand and let her argue.** That is
   what they were written for.
7. **ACCEPTED.** The framework-authorship question (Q013) is parked to 20 November. It needs no
   attention now.
8. **ACCEPTED — ships visible.** The patient-safety gap: known, stated, visible to the reviewer. **Default: ship it visible**
   and let the committee rule.

### C · Not decisions — work, or facts to obtain

9. **Indemnity premium** (Q001, due 21 Aug) — brief the brokers. The only zero in the model.
10. **Twelve faculty consents in writing** (Q003, due 31 Aug).
11. **Contactable names SQHN holds, and the 3-hour offering's conversion rate** (Q006, due 15 Sept).
12. **The live send test** — ten minutes, and it closes the last failure that could silently cost
    the reviewer an entire pass. See §8.
13. **One person who is not the author opens the walkthrough cold** — no longer urgent, since the
    link is held, but still the largest untested surface. — no explanation, two minutes,
    watch without helping. This remains the largest untested surface in the system.

**Go/no-go: 20 November 2026** — forty paid deposits, nine signed host-site MoUs, twelve consented
faculty. All three at once, or cohort 1 does not run.

## 7 · Invariants — never regress these

- **Canon is the only thing that is true, and only a human committee decision writes to it.** Never
  commit to `main` directly. Never edit `canon/**` except by pull request with CODEOWNER review. A
  workstream MAY add an open question it discovers; only the CCC may close one.
- **Never invent.** Every figure carries a live URL and an accessed date, or is written `NOT FOUND`
  with the search recorded. A plausible placeholder is the most dangerous output this system can
  produce.
- **The controlled vocabulary is enforced** (`canon/glossary.md`, checked by
  `engine/curriculum.py --vocabulary`). Programme not course; participant not student; artefact not
  assignment; observership not internship or placement. Quoting a source verbatim is exempt.
- **No participant personal data, credentials, tokens or private contact details in this
  repository.** It is public.
- **Reviewer answers are positional.** The walkthrough carries a fingerprint of the station order,
  and a build whose fingerprint does not match **refuses rather than guessing**. Do not work around
  a refusal — rebuild the page from the version she was sent, or ask for a fresh pass. Adding or
  reordering stops changes the fingerprint and is free only before a pass has begun.
- **The page must never claim something it cannot verify** — not delivery, not autosave, not
  confidence. Where it cannot know, it says so.
- **No decision is a one-way door.** The opportunity to course-correct, enhance or update stays
  open, and the reviewer is told so explicitly.
- **Changes reach the owner as a proved patch bundle he runs himself**, never as a push from an
  agent session. See §8.

## 8 · Verification protocol — before reporting anything done

Run all of these from the repository root. All must pass:

```
python3 engine/validate_ikr_pos.py
python3 engine/curriculum.py --self-test
python3 engine/curriculum.py --vocabulary
python3 engine/admissions.py --self-test
python3 engine/decision_capture.py --self-test
python3 engine/decision_interview.py --self-test
python3 engine/decision_interview.py --check
python3 engine/parameters.py --self-test
python3 engine/walkthrough.py --self-test
python3 engine/walkthrough.py --check
git diff --exit-code -- ccc/agenda.md ccc/control-room.html   # generated files committed
```

Last full run: **6 August 2026, all ten green**, working tree clean.

**Beyond the suite, three rules learned the hard way:**

- **A gate that can be satisfied by prose is not a gate.** Four checks written during the stress
  pass passed against a comment containing the asserted identifier, a button label sharing a phrase
  with the warning it guarded, and a local variable with the field's name. **Prove every new check
  fires by restoring the defect it guards and watching it go red.** Writing the check is not the
  work.
- **Nothing in this repository renders CSS or executes the page's JavaScript.** Layout and script
  defects are invisible to the suite. Drive the built page in a real browser before claiming it
  works.
- **The live send has never been exercised against real Netlify** with the acknowledgement logic
  that distinguishes a processed form from an ignored POST. Netlify answers both with 200; only the
  redirect differs, and that is not a documented contract. To settle it: open the site in a private
  window, answer two stops, leave a note, advance one part, then read the inbox. Green *sent — thank
  you* means it acknowledges; amber *not yet acknowledged* means either form detection is off or the
  check is too strict.

**Delivering a change to the owner.** Build a bundle with `engine/bundle.py` (currently on branch
`proposal/bundle-delivery-standard`): it runs the apply script twice against a fresh clone with git
stubbed, cuts against the current remote tip, and records the exact tree it promises. Verify the
bundle's patch-id equals your commit's before delivering. Bundles belong in the owner's workspace
archive folder alongside the previous forty-two, not loose in Downloads.

## 9 · Handback / relay protocol — identical in both directions

1. Commit everything with a descriptive message; push your proposal branch (never `main`).
2. **Prepend** a dated block to §5 STATE in the same format. Never edit an older block.
3. Update §6; surface any new blocker explicitly rather than folding it into prose.
4. Sync mirrors — if you are a Claude session, write the state summary to the Claude Project.
5. Brief the owner in one short message: what changed, what is next, what is blocked on him.

A returning agent resumes by reading this file top to bottom, then §5's newest block, then running
§8's suite to confirm the repository is where the file says it is.

**If the file and the repository disagree, the repository is right and the file is stale — fix the
file first, then continue.**
