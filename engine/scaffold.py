#!/usr/bin/env python3
"""Generate the QIPS Programme Office repository."""
import os, json, sys, textwrap
sys.path.insert(0, os.path.dirname(__file__))
from workstreams import WORKSTREAMS, DIRECTORATES, STATES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-07-28"

def w(path, content):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def yaml_list(items, indent=2):
    pad = " " * indent
    return "\n".join(f"{pad}- {i}" for i in items) if items else f"{pad}[]"

# ─────────────────────────────────────────────── CANON: the fact registry
FACTS = [
 # id, statement, status, owner workstream, source
 ("F001","The programme is a 12-month hybrid professional programme, not a course.","APPROVED","W02","Owner decision, decisions-log D4/D5"),
 ("F002","It is never described using the words course, class, lesson, student or module.","APPROVED","W13","Owner decision, decisions-log D4"),
 ("F003","The unit of the programme is the month: one eLearning release, one live faculty session, one small-group coaching call, one artefact.","APPROVED","W02","Owner decision, decisions-log; governing design principle"),
 ("F004","Artefacts are submitted four days before the coaching call so the coach arrives having read them.","APPROVED","W02","Programme architecture spec"),
 ("F005","Coaching is monthly, in small groups, on Zoom.","APPROVED","W06","Owner decision, decisions-log D5 as amended"),
 ("F006","The programme carries a 40-hour observership from month 3 to week 2 of month 4.","APPROVED","W04","Owner decision 2026-07-28, item 11"),
 ("F007","Participants attend a qualified host site in their own country; travel and accommodation are met by the participant or their sponsoring organisation.","APPROVED","W04","Owner decision 2026-07-28, item 12"),
 ("F008","Host sites are qualified against a published Host Site Standard derived from programme objectives, not from the characteristics of candidate sites.","APPROVED","W04","Owner decision, decisions-log"),
 ("F009","Coaching capability is built internally rather than bought in.","APPROVED","W06","Owner decision 2026-07-28, item 13"),
 ("F010","Measurement moves to month 3 and run charts to month 9.","APPROVED","W02","Owner decision 2026-07-28, item 14"),
 ("F011","Emmanuel and Dr Ajibike hold written authority to cut or merge content to protect the monthly cap.","APPROVED","W02","Owner decision 2026-07-28, item 6"),
 ("F012","Applications open October 2026 and close 31 December 2026.","APPROVED","W07","Owner decision 2026-07-28, item 4"),
 ("F013","Cohort 1 runs January to December 2027.","APPROVED","W10","Owner decision 2026-07-28, item 4"),
 ("F014","SQHN is the lead sponsor and the contracting entity that takes payment.","APPROVED","W17","Owner decision 2026-07-28, items 8 and 16"),
 ("F015","All other organisations are presented as Partners, led by Ruavira Collective Inc, QAI and The Arete Connoisseurs (TAC). The word consortium is retired.","APPROVED","W15","Owner decision 2026-07-28, item 8"),
 ("F016","The data controller is SQHN together with its partner organisations in each country of operation.","APPROVED","W17","Owner decision 2026-07-28, item 17"),
 ("F017","Brand identity is a mix of RCI and SQHN assets for now.","APPROVED","W13","Owner decision 2026-07-28, item 18"),
 ("F018","Admissions criteria are set on best practice.","APPROVED","W07","Owner decision 2026-07-28, item 15"),
 ("F019","Published time commitment is about 4 hours a week in an ordinary week and about 228 hours in total, derived from the curriculum rather than chosen for marketing.","APPROVED","W02","Owner decision 2026-07-28, item 5"),
 ("F020","Cohort 1 recruits in Nigeria, Ghana and Pakistan.","APPROVED","W01","Programme positioning, decisions-log"),
 ("F021","No fact may be published that has not been confirmed. Unconfirmed facts appear as visible placeholders, never as plausible invented values.","APPROVED","W17","Standing rule from the first session"),
 ("F022","ISQua involvement is at individual faculty level and is never described as institutional accreditation or endorsement.","APPROVED","W15","Claims-honesty audit"),
 ("F023","The first live faculty session is Saturday 9 January 2027, because the literal first Saturday falls in the New Year holiday weekend.","PROPOSED","W10","Recommended 2026-07-28, awaiting CCC"),
 ("F024","Published price ladder: International USD 3,000, UMIC 1,200, LMIC institutional 900, LMIC individual 600, LIC 400.","PROPOSED","W16","Council recommendation 2026-07-28, NOT APPROVED"),
 ("F025","Cohort 1 target 50, hard floor 40 paid deposits, cap 64.","PROPOSED","W07","Council recommendation 2026-07-28, NOT APPROVED"),
 ("F026","Per-learner indemnity above USD 75 triggers deferral of the observership to cohort 2 and an LMIC price of USD 475.","PROPOSED","W16","Council conditional ruling 2026-07-28, NOT APPROVED"),
 ("F027","Go/no-go kill date is 20 November 2026: 40 paid deposits, 9 signed host-site MoUs, 12 consented faculty, all three at once.","PROPOSED","W17","Council recommendation 2026-07-28, NOT APPROVED"),
]

facts_yaml = ["# CANON — the fact registry.",
 "# The single source of truth for what has been established about this programme.",
 "#",
 "# STATUS values:",
 "#   APPROVED   the coordinating committee has ratified it. Binding on every workstream.",
 "#   PROPOSED   a workstream or council recommends it. NOT binding. Never publish it.",
 "#   SUPERSEDED replaced by a later fact. Kept for provenance. Never deleted.",
 "#",
 "# Only two things write to this file: a CCC decision, and a supersession recorded by the CCC.",
 "# No workstream may edit it directly.",
 f"# Last promotion: {TODAY}", "", "facts:"]
for fid, stmt, status, owner, src in FACTS:
    facts_yaml += [f"  - id: {fid}",
                   f"    statement: \"{stmt}\"",
                   f"    status: {status}",
                   f"    owner: {owner}",
                   f"    source: \"{src}\"",
                   f"    established: {TODAY}", ""]
w("canon/facts.yaml", "\n".join(facts_yaml))

# ─────────────────────────────────────────────── CANON: glossary
w("canon/glossary.md", """# Controlled vocabulary

Binding on every workstream, every agent and every published artefact. A term on the
left is the only permitted form. A term on the right is banned and is checked for by
the verification stage of every workstream run.

| Use this | Never this | Why |
|---|---|---|
| programme | course | The owner's decision: a programme signals sustained commitment from the learner and their sponsor. |
| phase, topic | module, unit | "Module" reads as a course component and is banned with "course". |
| participant | student, delegate | Participants are working professionals, not students. |
| live session | class, lecture, webinar | The live session is taught and interactive. |
| coaching call | tutorial, office hours | Coaching is a distinct instructional modality with its own standard. |
| observership | internship, placement, attachment | "Internship" implies transferred clinical liability and is a legal exposure, not a style preference. |
| host site | placement site, partner hospital | Host sites are qualified against a published standard. |
| cohort | class, intake year | |
| artefact | assignment, homework | The artefact is a piece of the capstone, produced for use, not for marking. |
| capstone | final project, dissertation | |
| SQHN and Partners | consortium, the consortium | SQHN is the lead sponsor; everyone else is a partner. Retired 28 July 2026. |
| faculty affiliated with ISQua | ISQua-accredited, ISQua-certified, in partnership with ISQua | Involvement is at individual faculty level. Anything stronger is a claim the programme cannot support. |

## Claims that may never be made
- Any guarantee of employment, promotion or income.
- Any accreditation, endorsement or recognition not confirmed in writing by the body named.
- Any scarcity or urgency claim without a real, approved cohort cap.
- Any statistic without a source, an accessed date and a live URL in the evidence registry.
- Any number that was not supplied by a named person or a cited source. A plausible
  placeholder is the most dangerous output this system can produce.
""")

# ─────────────────────────────────────────────── CANON: dependencies
dep_lines = ["# Which workstreams must have APPROVED facts before another can finalise.",
             "# The engine refuses to promote a dossier whose upstream dependencies are unapproved.",
             "", "dependencies:"]
for ws in WORKSTREAMS:
    dep_lines.append(f"  {ws['id']}:  # {ws['name']}")
    dep_lines.append(f"    depends_on: {ws['depends_on'] if ws['depends_on'] else '[]'}")
    blocks = [o['id'] for o in WORKSTREAMS if ws['id'] in o['depends_on']]
    dep_lines.append(f"    blocks: {blocks if blocks else '[]'}")
w("canon/dependencies.yaml", "\n".join(dep_lines) + "\n")

# ─────────────────────────────────────────────── CANON: open questions
w("canon/open-questions.yaml", """# Every unresolved question in the programme, with an owner and a blocking status.
# A workstream may add questions it discovers. Only the CCC may close one.
# BLOCKING means cohort 1 cannot proceed without it.

questions:
  - id: Q001
    question: "What is the per-learner medical indemnity and public liability premium across Nigeria, Ghana and Pakistan?"
    owner: W17
    blocking: true
    blocks: [W16, W04]
    due: 2026-08-21
    note: "The only zero in the financial model. Gates the price and the observership."

  - id: Q002
    question: "What is the exact certificate title, the awarding entity, any post-nominals, and what CPD recognition can be claimed?"
    owner: W03
    blocking: true
    blocks: [W13, W14, W16]
    due: 2026-08-31
    note: "The credential precedes the price. Nothing markets until this exists."

  - id: Q003
    question: "Who are the twelve faculty, and have they consented in writing to be named?"
    owner: W05
    blocking: true
    blocks: [W14]
    due: 2026-08-31

  - id: Q004
    question: "What is the signed partner agreement between SQHN, RCI, QAI and TAC — revenue share, IP, exit, and who may sign a host-site MoU?"
    owner: W15
    blocking: true
    blocks: [W04, W12, W16]
    due: 2026-09-30
    note: "Without a named signatory, host-site recruitment cannot legally start."

  - id: Q005
    question: "What is QAI's full registered name, identity and programme role?"
    owner: W15
    blocking: true
    blocks: [W13, W14]
    due: 2026-08-15
    note: "QAI is on the brochure cover with no verified identity behind it."

  - id: Q006
    question: "How many contactable names does SQHN hold, and what did the existing 3-hour course convert at?"
    owner: W14
    blocking: true
    blocks: [W07, W16]
    due: 2026-09-15
    note: "Cohort size is a funnel output, not an opinion. Nobody has the denominator."

  - id: Q007
    question: "Is the Industrial Training Fund reimbursement real, and on what terms?"
    owner: W16
    blocking: false
    due: 2026-09-30
    note: "Booked at zero until primary-verified with the ITF itself."

  - id: Q008
    question: "What is the approved affiliation wording from Shifa International Hospitals and from ISQua?"
    owner: W15
    blocking: true
    blocks: [W14]
    due: 2026-09-30

  - id: Q009
    question: "What is the data retention period and who is the data-protection contact?"
    owner: W17
    blocking: true
    blocks: [W09, W14]
    due: 2026-09-30

  - id: Q010
    question: "What is the programme called?"
    owner: W13
    blocking: true
    blocks: [W14, W03]
    due: 2026-08-31
""")

# ─────────────────────────────────────────────── WORKSTREAM WORKSPACES
for ws in WORKSTREAMS:
    d = ws["id"]
    dn = DIRECTORATES[ws["d"]][0]
    brief = f"""# {ws['id']} — {ws['name']}

**Directorate {ws['d']} · {dn}**
Maps to the owner's original list: *{ws['maps_to']}*
Proposed cohort-1 position: **{ws['cohort1']}**

## The question this workstream exists to answer

> {ws['owner_question']}

## What it must produce

{chr(10).join('- ' + o for o in ws['outputs'])}

## Research lenses

Each run fans out parallel researchers, one per lens. A lens is a way of looking, not a
topic — two researchers on the same topic with different lenses find different things.

{chr(10).join(f'{i+1}. {l}' for i, l in enumerate(ws['lenses']))}

## Benchmarks it must compare against

Every dossier from this workstream carries a comparison table against these, with a
column for what each does, a column for what we would do differently, and a column
stating why the difference is an improvement rather than a shortcut.

{chr(10).join('- ' + b for b in ws['benchmarks'])}

## Dependencies

Cannot finalise until these workstreams have APPROVED facts: **{', '.join(ws['depends_on']) if ws['depends_on'] else 'none — this workstream can start immediately'}**

## Standing note

{ws['note']}

## How this workstream runs

It runs the standard seven-stage engine (`engine/README.md`). It never edits canon.
It reads canon, works in `working/`, and emits a dossier to `dossiers/` for the CCC.
"""
    w(f"workstreams/{d}/brief.md", brief)
    w(f"workstreams/{d}/state.yaml",
      f"id: {d}\nname: \"{ws['name']}\"\ndirectorate: {ws['d']}\n"
      f"state: DORMANT\ncohort1_scope: {ws['cohort1']}\nlast_run: null\nruns: 0\n"
      f"dossiers_submitted: 0\ndossiers_approved: 0\nconsecutive_dry_rounds: 0\n"
      f"blocked_by: {ws['depends_on'] if ws['depends_on'] else '[]'}\n")
    w(f"workstreams/{d}/questions.yaml",
      f"# Questions owned by {d}. The workstream may add; only the CCC may close.\nquestions: []\n")
    for sub in ("working", "dossiers", "inbox"):
        os.makedirs(os.path.join(ROOT, f"workstreams/{d}/{sub}"), exist_ok=True)
        w(f"workstreams/{d}/{sub}/.keep", "")

# ─────────────────────────────────────────────── CCC
w("ccc/charter.md", """# Central Coordinating Committee — charter

The CCC is the only part of this system that requires a human. Everything else runs
autonomously and in loops. The CCC's job is not to do the work; it is to decide, and
to be the only route by which anything becomes true.

## Standing membership
[TO CONFIRM: named members and their alternates]
Chair: [TO CONFIRM]. Quorum: [TO CONFIRM]. A decision needs a chair plus quorum.

## Decision rights

The CCC alone may:
- promote a PROPOSED fact to APPROVED, which makes it binding on all seventeen workstreams;
- supersede an APPROVED fact, which requires recording what replaced it and why;
- close an open question;
- set or change a workstream's cohort-1 scope (NOW / NEXT / LATER);
- approve a published price, a published claim, or anything that carries an external commitment;
- overrule a council verdict.

No workstream, no agent and no automation may do any of these. A workstream that
believes canon is wrong raises a supersession request; it does not edit canon.

## What the CCC receives

Never raw research. Only a **decision dossier**, in the fixed shape defined in
`engine/schemas/dossier.md`. A dossier that does not carry a benchmark table, a council
verdict and a passed verification report is returned unread — not because the content is
wrong, but because accepting it would teach the system that the gates are optional.

## The four verdicts

**APPROVE** — the recommendation becomes canon. Its facts are promoted, its open
questions closed, and every dependent workstream is woken.

**AMEND** — approve with a named change. The amendment is recorded as the CCC's own
fact, attributed to the CCC and not to the workstream.

**REJECT** — with a stated reason. The reason is written back into the workstream's brief
as a new constraint, so the next run cannot repeat the mistake. A rejection without a
reason is the one thing that breaks the loop.

**DEFER** — with a named condition and a date. Deferral is a decision and is minuted.

## Cadence

Weekly during the application window (October to December 2026), fortnightly otherwise.
The agenda assembles itself: `ccc/agenda.md` is regenerated from workstream state before
each sitting. An agenda item that has waited more than two sittings escalates and is
listed first.

## The rule that keeps the system honest

If the CCC finds itself approving a dossier it does not have time to read, the answer is
not to read faster. It is to send it back and reduce how many workstreams are active at
once. Seventeen workstreams can run. Seventeen dossiers cannot be decided in one sitting.
""")

roadmap = ["# Cohort scope — what ships when.",
           "# NOW = cohort 1 (January 2027). NEXT = cohort 2 (2028). LATER = cohort 3 and the regional-centre model.",
           "# Only the CCC may move a workstream between columns.", "", "cohorts:",
           "  cohort_1:", "    label: \"January 2027 — prove the monthly cycle and the observership\"",
           "    starts: 2027-01", "    workstreams:"]
for ws in WORKSTREAMS:
    if ws["cohort1"] == "NOW":
        roadmap.append(f"      - {ws['id']}  # {ws['name']}")
roadmap += ["  cohort_2:", "    label: \"2028 — compound the credential: alumni, coach pipeline, published outcomes\"",
            "    workstreams:"]
for ws in WORKSTREAMS:
    if ws["cohort1"] == "NEXT":
        roadmap.append(f"      - {ws['id']}  # {ws['name']}")
roadmap += ["  cohort_3_and_beyond:", "    label: \"Regional centres, advanced tier, institutional programme\"",
            "    workstreams: []", "",
            "# The vision, held deliberately even where it does not ship in cohort 1:",
            "vision:",
            "  - \"A published Host Site Standard that becomes regional infrastructure, not just a placement list.\"",
            "  - \"A coach cadre grown from graduates, so cohort N teaches cohort N+1.\"",
            "  - \"A capstone dataset across three countries that nobody else holds.\"",
            "  - \"An advanced tier above the foundation programme, and a credential ladder between them.\"",
            "  - \"Regional centres that qualify and monitor their own host sites under the same standard.\"",
            "  - \"External evaluation of the programme itself, on the same terms it teaches participants to accept.\""]
w("ccc/roadmap.yaml", "\n".join(roadmap) + "\n")
os.makedirs(os.path.join(ROOT, "ccc/minutes"), exist_ok=True)
w("ccc/minutes/.keep", "")

print(f"scaffold written to {ROOT}")
print(f"  {len(WORKSTREAMS)} workstreams across {len(DIRECTORATES)} directorates")
print(f"  {len(FACTS)} facts seeded ({sum(1 for f in FACTS if f[2]=='APPROVED')} approved, {sum(1 for f in FACTS if f[2]=='PROPOSED')} proposed)")
