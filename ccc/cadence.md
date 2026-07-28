# The cadence — how the system runs when nobody starts it

Not yet switched on. It creates recurring sessions that consume budget on a schedule, so the
committee turns it on deliberately rather than finding it already running.

## What it would do

A scheduled task fires on a cadence. Each firing starts a fresh session that:

1. reads every `workstreams/*/state.yaml` and `canon/dependencies.yaml`;
2. selects the runnable set — dependencies satisfied, not AWAITING_CCC, not dry;
3. **caps the cycle at three workstreams**, ordered: blocking open questions first, then
   workstreams whose dependencies just cleared, then cohort-1 scope, then the rest;
4. runs `engine/workstream-engine.js` on each;
5. writes dossiers, updates state, adds new open questions;
6. regenerates `ccc/agenda.md` and `ccc/control-room.html` and mirrors both to the project;
7. notifies the chair **only** if something needs a decision or a BLOCKING finding appeared.

A quiet week produces no notification. That is the intended behaviour, not a failure.

## Proposed schedule

| Period | Cadence | Why |
|---|---|---|
| Now to 30 September 2026 | Weekly, Monday 06:00 WAT | Nine weeks to applications opening. Blocking questions dominate; the committee needs a decision surface every week. |
| October to December 2026 | Weekly, Monday 06:00 WAT | The application window. Recruitment, admissions and operations all move at once. |
| January 2027 onward | Fortnightly | Cohort 1 is running. Delivery displaces design. |

Monday 06:00 West Africa Time is 05:00 UTC, so `0 5 * * 1`.

## The three settings that matter

**Three workstreams per cycle.** Raising it does not raise throughput, because the bottleneck
is the committee, not the engine. If dossiers queue for more than two sittings, the correct
response is to lower this number, not to read faster.

**Advisors: 3 by default, 5 for decisions that are hard to reverse.** Pricing, the certificate
title, the partner agreement and anything with an external commitment get five.

**Notify only on decisions and blocking findings.** A system that reports every cycle trains
the committee to stop reading it.

## To switch it on

Ask, and the task is created with the schedule above. To stop it, ask again — it is a single
scheduled task, deleted in one step, and everything it produced stays in the repository.

## The manual alternative

Nothing depends on the schedule. A cycle can be run by hand at any time by invoking the
`qips-programme-office` skill and naming the workstreams. The schedule only removes the need
for someone to remember.
