# The CCC Decision Dossier

The only artefact a workstream may put in front of the Central Coordinating Committee.
One shape, every time, from all seventeen workstreams. A dossier missing any numbered
section is returned unread.

Returning it unread is not pedantry. The gates are what make the committee's approval mean
something; accepting one dossier without them teaches the system that the gates are optional,
and the next one arrives without them too.

---

```markdown
# DOSSIER {WID}-{NN} — {workstream name}
**For decision on {date} · Prepared by workstream {WID} · Run {n} · Verification: {PASS | PASS WITH FINDINGS}**

## 1. The decision requested
One sentence. What the committee is being asked to decide — not what the workstream studied.

## 2. Why it is on the agenda now
What it blocks, what it costs to defer another cycle, and which open questions it closes.

## 3. What canon already establishes
The APPROVED facts this decision must be consistent with, by id. If the recommendation
requires superseding one, say so here, in bold, and say which.

## 4. Benchmark
| Comparator | What they do | What we would do differently | Why that is better, not just cheaper | Source |
Minimum four named comparators. Every row carries a URL and an accessed date. "We would do
the same" is a legitimate entry — copying a proven pattern is a decision, and novelty for
its own sake is a cost.

## 5. The options
Two or three, each genuinely defensible. For each: what it is, the case for, the case
against, what it costs, and whether it belongs in cohort 1 or later.
One option with two strawmen is the commonest way an options paper lies. The verification
stage checks for it.

## 6. Council verdict
Where the advisors converged independently — high-confidence signal.
Where they genuinely clashed, both sides presented rather than smoothed.
Whether the chairman overruled the majority, and why.

## 7. Recommendation
A decision, not a summary. "It depends" is a failure of the workstream, not a property of
the problem.

## 8. Conditions
Falsifiable tests with dates. "Ensure quality is maintained" is not a condition.
"Nine host-site MoUs signed by 20 November 2026" is.

## 9. What becomes canon if you approve
The exact fact statements to be promoted, written so that someone reading only that line in
six months understands it. Plus any fact this supersedes.

## 10. What this unblocks
Which workstreams wake up, and which open questions close.

## 11. Innovation opportunities
Where the research found every comparator doing the same thing, and there is room to do
better. Openings that can be pointed at — not wishes.

## 12. What we could not establish
The honest gaps. What was searched for and not found, and what was tried.
A committee that never sees this section is being managed rather than informed.

## 13. Verification report
Verdict, claims checked, claims that failed, and every SERIOUS or BLOCKING finding with
its disposition. A dossier with an unresolved BLOCKING finding does not reach the committee.
```

---

## Machine-readable header

Every dossier carries this front matter so the control room and the agenda can be
regenerated without anyone reading the prose.

```yaml
dossier: W13-01
workstream: W13
run: 1
prepared: 2026-07-28
verification: PASS WITH FINDINGS
blocking_findings_open: 0
decision_requested: "Adopt the recommended programme name and credential architecture"
closes_questions: [Q010]
unblocks: [W14, W03]
supersedes_facts: []
promotes_facts: 3
state_after_submission: AWAITING_CCC
```
