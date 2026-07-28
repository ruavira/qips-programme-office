# How the Programme Office works

Seventeen workstreams. One committee. Everything between them runs without a human in it.

The design problem is not "how do we do more work." It is: **how does a small team stay the
decision-maker of a programme that is producing more analysis than any small team can read.**
Everything below exists to answer that.

---

## 1. The shape

```
                        ┌─────────────────────────────┐
                        │   CANON  (read-mostly)      │
                        │   facts · evidence ·        │
                        │   glossary · dependencies · │
                        │   open questions            │
                        └──────────┬──────────────────┘
                    reads          │          promotes
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐        ...     ┌────▼────┐
   │   W01   │  │   W02   │  │   W03   │   17 of these  │   W17   │
   │workspace│  │workspace│  │workspace│                │workspace│
   └────┬────┘  └────┬────┘  └────┬────┘                └────┬────┘
        │            │            │                          │
        └────────────┴─────┬──────┴──────────────────────────┘
                           │  decision dossiers only
                    ┌──────▼───────┐
                    │     CCC      │  ◄── the only human in the system
                    │  approve /   │
                    │  amend /     │
                    │  reject /    │
                    │  defer       │
                    └──────┬───────┘
                           │
                    promotes to canon,
                    wakes dependents
```

**Canon is the only thing that is true.** A workstream reads it and may never write to it. The
sole route into canon is a CCC decision. This is the rule that makes seventeen autonomous
teams safe: they cannot contradict each other, because they cannot change the shared truth.

**A workstream workspace is disposable.** Research, drafts, dead ends, superseded options —
all of it lives in `working/` and none of it binds anyone. The only thing that leaves a
workspace is a dossier.

**The CCC never sees research.** It sees a dossier, in one fixed shape, every time.

---

## 2. The seven stages every workstream runs

Identical for all seventeen. The workstream supplies its question, its lenses, its benchmarks.
The engine supplies the rigour.

**1 · SCOUT.** Read canon and the workspace. What is already established, what did previous
runs of this workstream conclude, what did the CCC reject and why. A rejection reason from a
past sitting is a hard constraint on this run — this is how the loop learns instead of
re-proposing what was already refused.

**2 · RESEARCH — fan out.** One agent per lens, in parallel. A lens is *a way of looking*, not
a topic. Three researchers pointed at the same subject through different lenses find different
things; three researchers given three subtopics just divide the same shallow sweep into
thirds. Every finding carries a URL and an accessed date or is written as NOT FOUND. Each
researcher is also asked for **innovation openings**: places where every comparator does the
same thing, leaving room to do better.

**3 · BENCHMARK.** A fixed table: comparator, what they do, what we would do differently, and
the column that does the real work — *why that difference is an improvement rather than a
shortcut*. "We would do the same" is a legitimate row. Copying a proven pattern is a decision;
novelty for its own sake is a cost.

**4 · OPTIONS.** Two or three genuinely different approaches, each defensible by someone
reasonable, each with its own case-for and case-against, its cost, and whether it belongs in
cohort 1 or later. One option with two strawmen is the most common way an options paper lies,
and the verification stage checks for it explicitly.

**5 · COUNCIL.** Independent advisors — Contrarian, First Principles, Executor, Outsider,
Expansionist — answer without seeing each other's work, then a chairman synthesises into a
decision. Each advisor must state the strongest objection to their own position; that is the
part that makes the chairman's job possible. The chairman may overrule the majority and must
say so when they do.

**6 · VERIFY.** A fresh agent with no stake, told to assume the authors were careless. It
fetches the cited URLs and checks the pages actually say what the dossier claims. It hunts
invented values, banned vocabulary, overclaiming, internal contradiction, undeliverable
timelines and straw options. BLOCKING findings send the dossier back without it ever reaching
the committee.

**7 · DOSSIER.** The fixed shape in `schemas/dossier.md`. Nothing else goes to the CCC.

---

## 3. Why it loops

A workstream is not a task that completes. It is a **state machine that keeps running until
its question stops producing new answers.**

```
DORMANT → SCOUTING → RESEARCHING → IN_COUNCIL → VERIFYING → AWAITING_CCC
                          ▲                          │              │
                          │      BLOCKING findings   │              │
                          └──────────────────────────┘              │
                          ▲                                         │
                          │            REJECT / AMEND               │
                          └─────────────────────────────────────────┘
                                                                    │ APPROVE
                                                              ┌─────▼─────┐
                                                              │ APPROVED  │
                                                              └───────────┘
```

**Loop-until-dry, not loop-until-count.** A workstream keeps cycling until **two consecutive
rounds surface nothing the previous round did not already have.** Counting rounds misses the
tail; dryness is the only honest stopping rule for discovery.

**Rejection is fuel.** A CCC rejection reason is written back into the workstream's brief as a
standing constraint. The next run cannot repeat the mistake, because the mistake is now part
of the brief. This is why a rejection without a stated reason is the single thing that breaks
the system.

**Approval wakes the neighbours.** When a fact is promoted, every workstream that declared a
dependency on it moves from BLOCKED to DORMANT and becomes eligible for the next cycle. The
dependency graph in `canon/dependencies.yaml` is what makes seventeen independent loops behave
like one programme.

---

## 4. Who runs it when nobody is watching

A scheduled task wakes the Programme Office on a cadence. Each waking:

1. reads every workstream's `state.yaml` and the dependency graph;
2. selects the runnable set — dependencies satisfied, not awaiting the CCC, not dry;
3. caps concurrency to what the committee can actually decide (default: **three workstreams
   per cycle**, because the binding constraint is committee attention, not compute);
4. runs the engine on each;
5. regenerates `ccc/agenda.md` and pushes it to the project;
6. notifies the chair only when something needs a decision or a blocking finding appeared.

The cap is the important line. Seventeen workstreams *can* run. Seventeen dossiers cannot be
decided in one sitting, and a committee that rubber-stamps because it is overwhelmed is worse
than no committee.

---

## 5. What stays human

Only these, and deliberately:

- promoting a fact to canon, and superseding one;
- closing an open question;
- setting cohort scope — what ships in cohort 1 versus what waits;
- approving any published price, claim or external commitment;
- overruling a council;
- deciding *not* to run a workstream at all.

Everything else — research, benchmarking, option generation, adversarial review,
verification, drafting, scheduling, agenda assembly, dependency management — runs without
asking.

---

## 6. Running it by hand

```
Workflow({
  scriptPath: "engine/workstream-engine.js",
  args: {
    workstreams: [ /* workstream objects from engine/workstreams.py */ ],
    canon: "<the APPROVED facts, as text>",
    advisors: 3,          // 5 for a decision that is hard to reverse
    lensesPerStream: 3,   // 4 or 5 for a foundational workstream
  }
})
```

Cost scales as `workstreams × (lenses + 1 + advisors + 1 + 1)`. Two workstreams at three
lenses and three advisors is eighteen agents. A single foundational workstream at five lenses
and five advisors is thirteen. Budget the committee's attention first and the agents second.
