# Central Coordinating Committee — charter

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
