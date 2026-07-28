# The QIPS Programme Office

**How a small team stays the decision-maker of a programme too large for a small team to read.**
Design memo · 28 July 2026

---

## The problem, stated properly

You asked how to manage a large body of work with a small team. That framing is almost right,
but the constraint is narrower than it looks and worth naming exactly, because the whole design
follows from it.

The scarce resource is not effort. It is not money, and with agents it is certainly not
analysis. **The scarce resource is your attention as the deciding body.** Seventeen
workstreams can research, benchmark, argue and verify indefinitely without you. But every one
of them eventually produces something only you can settle, and the moment the committee starts
approving things it has not properly read, the entire apparatus becomes a very expensive way
of generating confident mistakes.

So the system is built backwards from that: not "how do we produce more" but "how do we make
sure that what reaches the committee is worth the committee's time, and that everything else
resolves itself."

---

## 1. How many components — and the five you did not name

Your eleven are real. Ten of them are workstreams; one is not.

**(k) the coordinating committee is not a component.** It is the gate every component reports
to. Treating it as a workstream is the mistake that quietly turns a governing body into
another working group, and then nobody governs. It gets a charter, decision rights and a
cadence, not a research brief.

The remaining ten unpack into twelve, because two of yours each contain two different jobs.
**(c) faculty and observership** is really two — who teaches, and where people go to observe;
they share nothing but a sentence in your list. And **(b) instructional design through to
post-programme community** carries a whole second discipline at its far end: what happens to
someone after they graduate is a retention-and-alumni problem, not a curriculum problem, and
it is the one that makes the credential compound.

Then five more that nobody has, and each of which fails the programme quietly if left unowned:

**W03 · Assessment, Certification and Credentialing.** There is currently no certificate. Not
an unfinished one — none. No title, no awarding entity, no post-nominals, no assessment
blueprint, no standard-setting method, no CPD recognition, no appeals policy. Your pricing
council put it bluntly: the credential is the product, and no price exists before it does. A
twelve-month programme whose graduates cannot say precisely what they hold is not a programme;
it is a long series of meetings.

**W07 · Admissions, Recruitment and Selection.** Eligibility, the application itself, how you
choose between two applicants, employer release, scholarships, and the funnel. You decided
admissions would be "set on best practice" — that is a direction, not a design. And the
verification pass found something sharper: nobody knows the recruitment denominator. Five
advisors argued about whether cohort 1 should be twenty-five or eighty without anyone asking
how many contactable names SQHN actually holds. Cohort size is a funnel output, not an
opinion.

**W11 · Quality Assurance and Programme Evaluation.** How you know the programme works, and
how you would find out if it did not. A programme that teaches hospitals to measure, publish
and improve, and does not do those things to itself, has a credibility problem that will be
noticed by exactly the audience whose opinion matters most.

**W12 · Data, Outcomes and Research Assets.** Fifty capstone improvement projects with
baselines across three health systems is a dataset nobody else in the world holds. It buys
publications, ISQua standing and the conversation with NHIA. It requires consent language in
the participant agreement *before* cohort 1 starts. Miss that window and the asset is gone,
not delayed.

**W17 · Governance, Legal, Risk and Data Protection.** Who is legally responsible, in which
jurisdiction, when something goes wrong. This is where the unquoted per-learner indemnity
lives — the single zero in your financial model that gates both the price and the observership.
It is also where the missing partner agreement sits: SQHN, RCI, QAI and TAC have no revenue
share, no IP ownership, no exit terms and, critically, **no named signatory**, which means
nobody currently has the authority to sign a host-site MoU. Your Host Site Standard is
excellent and cannot yet be applied to a single real hospital.

**Seventeen workstreams, four directorates.**

| | Directorate | Workstreams |
|---|---|---|
| D1 | Programme — what it actually is | W01 Needs Assessment · W02 Curriculum · **W03 Assessment and Certification** · W04 Practicum and Observership |
| D2 | People — who delivers and who learns | W05 Teaching Faculty · W06 Coaching Faculty · **W07 Admissions** · W08 Learner Success and Alumni |
| D3 | Platform and Operations — how it runs | W09 Technology · W10 Cohort Operations and the Global Calendar · **W11 Quality Assurance** · **W12 Data and Research Assets** |
| D4 | Business and Governance — what makes it viable | W13 Brand and Naming · W14 Marketing and Enrolment · W15 Partnerships and Accreditation · W16 Pricing and Finance · **W17 Governance, Legal and Risk** |

The directorate layer exists for one reason: seventeen items is above the number a committee
can hold in its head, and four is not.

---

## 2. What each workstream's team actually does

One engine, seventeen configurations. Each workstream supplies its question, its research
lenses and its named benchmarks; the engine supplies the rigour. Seven stages:

**Scout.** Read canon and the workspace. What is already true, what previous runs concluded,
and — the important one — *what the committee rejected and why*. A rejection reason from a past
sitting becomes a hard constraint on this run. This is how the loop learns instead of
re-proposing what was already refused.

**Research — fan out.** One agent per lens, in parallel. A lens is a *way of looking*, not a
topic. Three researchers pointed at the same subject through different lenses find different
things; three researchers handed three subtopics just divide one shallow sweep into thirds.
Every finding carries a live URL and an accessed date, or is written NOT FOUND. Each is also
asked for **innovation openings**: places where every comparator does the same thing, leaving
room to do better.

**Benchmark.** A fixed table — comparator, what they do, what we would do differently, and the
column that does the real work: *why that difference is an improvement rather than a shortcut.*
"We would do the same" is a legitimate row. Copying a proven pattern is a decision; novelty for
its own sake is a cost.

**Options.** Two or three genuinely different approaches, each defensible by someone
reasonable, each with a case for, a case against, a cost, and a cohort-1-or-later position. One
option flanked by two strawmen is the commonest way an options paper lies, and the verification
stage checks for it by name.

**Council.** Independent advisors — Contrarian, First Principles, Executor, Outsider,
Expansionist — answer without seeing each other's work, then a chairman synthesises into a
decision. Each advisor must state the strongest objection to their own position. That
requirement is what makes the chairman's job possible, and it is the thing advisors otherwise
never do.

**Verify.** A fresh agent with no stake, instructed to assume the authors were careless. It
fetches the cited URLs and checks the pages say what the dossier claims. It hunts invented
values, banned vocabulary, overclaiming, internal contradiction, undeliverable timelines and
straw options. A BLOCKING finding sends the dossier back before the committee ever sees it.
On the pricing pack, this stage returned FAIL and found two arithmetic errors that had changed
the model's own conclusions. It earns its place.

**Dossier.** One fixed shape, thirteen sections, every time, from all seventeen workstreams.

---

## 3. Why it loops, and how it stops

A workstream is not a task that completes. It is a state machine that runs until its question
stops producing new answers.

```
DORMANT → SCOUTING → RESEARCHING → IN_COUNCIL → VERIFYING → AWAITING_CCC → APPROVED
              ▲                          │                        │
              │       BLOCKING findings  │      REJECT / AMEND    │
              └──────────────────────────┴────────────────────────┘
```

Three properties make this work rather than spin:

**Loop-until-dry, not loop-until-count.** A workstream stops when two consecutive rounds
surface nothing the previous round did not already have. Counting rounds misses the tail;
dryness is the only honest stopping rule for open-ended discovery.

**Rejection is fuel.** A committee rejection reason is written back into the workstream's brief
as a standing constraint, so the next run cannot repeat the refused answer. This makes a
rejection without a stated reason the single input that breaks the system — worth saying out
loud at the first sitting.

**Approval wakes the neighbours.** When a fact is promoted, every workstream that declared a
dependency on it moves from BLOCKED to DORMANT and becomes eligible for the next cycle. The
dependency graph is what makes seventeen independent loops behave like one programme instead of
seventeen programmes.

---

## 4. The repository — you asked, and yes, but with one rule

Yes: one central repository, with per-team workspaces pulling from and contributing to it. But
the naive version of that fails within a month, because seventeen teams writing to shared truth
produces contradiction faster than anyone can reconcile it. The discipline that prevents it is
a single rule:

> **Canon is the only thing that is true, and only the committee writes to it.**

```
canon/                       ← read-mostly. One writer: a CCC decision.
  facts.yaml                 ← 27 facts, each APPROVED or PROPOSED, with source and owner
  glossary.md                ← controlled vocabulary and the claims that may never be made
  dependencies.yaml          ← who waits on whom, who is unblocked by whom
  open-questions.yaml        ← every unknown, with an owner, a blocking flag and a date
  inventory.md               ← every artefact built so far, filed to its owning workstream
  evidence/                  ← citations, URLs, accessed dates

workstreams/W03/             ← ×17. Disposable. Binds nobody.
  brief.md                   ← question, outputs, lenses, benchmarks, and past rejections
  state.yaml                 ← state, runs, dry-round counter, blocked-by
  working/                   ← research, drafts, dead ends
  dossiers/                  ← the only thing that leaves

ccc/
  charter.md · agenda.md · minutes/ · roadmap.yaml · cadence.md · control-room.html
```

A workstream reads canon and may never edit it. If it believes canon is wrong it raises a
supersession request — it does not quietly change the shared truth. Facts are superseded, never
deleted, so the provenance of every reversal survives.

This is also what makes the teams genuinely autonomous. They can run in parallel without
coordination *because* they cannot contradict each other.

---

## 5. What ships in cohort 1, and what the vision is

Sixteen of the seventeen are cohort-1 workstreams. Only W08, learner success and alumni,
formally waits — and even there the retention half belongs in cohort 1, because the council
established that attrition is a revenue line and not a quality metric. What waits is the alumni
network, which cannot exist before there are alumni.

Holding the vision deliberately, even where it does not ship:

- A published Host Site Standard that becomes regional infrastructure — a qualified-site
  register mapped onto NHIA's 7,000+ facilities — rather than a placement list.
- A coach cadre grown from graduates, so cohort N teaches cohort N+1 and the largest cost line
  in the model becomes the largest asset.
- A capstone dataset across three health systems that nobody else holds.
- An advanced tier above the foundation programme, with a credential ladder between them. This
  is why the naming workstream matters now: a name with no room above it forces a rebrand in
  two years.
- Regional centres qualifying and monitoring their own host sites under the same standard.
- External evaluation of the programme itself, on the same terms it teaches participants to
  accept.

---

## 6. What you are missing

Beyond the five unowned workstreams, five structural things — none of which is a component, all
of which decide whether the components add up.

**A denominator.** Every conversation about cohort size so far has been an opinion. How many
contactable names does SQHN hold, and what did the ₦50,000 course convert at? Until that number
exists, "fifty participants" is a wish. It is now question Q006, owned by W14, due 15 September.

**A kill date.** The council set one — 20 November 2026, requiring forty paid deposits, nine
signed host-site MoUs and twelve consented faculty, all three at once. What matters is less the
date than the principle: deferral in November is a manageable decision, and discovering the
same shortfall in March with faculty booked and sites committed is not.

**A partner agreement.** Four organisations, one P&L, no revenue share, no IP ownership, no
exit terms, no named signatory. This blocks host-site recruitment today, and it becomes an
argument in cohort 2 if it is not settled in cohort 1.

**A cap on committee load.** Three workstreams per cycle. Not because the engine cannot run
seventeen — it can — but because a committee that rubber-stamps because it is overwhelmed is
worse than no committee. If dossiers queue more than two sittings, lower the number rather than
reading faster.

**Someone whose job is to say no.** You named Emmanuel and Dr Ajibike for content. The same
authority is needed for scope. Seventeen workstreams generating good ideas will produce more
good ideas than a first cohort can absorb, and every one of them will be defensible.

---

## 7. Two things I would push back on

**Autonomy is not the same as unsupervised.** You asked for everything except the committee to
run autonomously, and it does. But the verification stage exists precisely because autonomous
research is confidently wrong at a low, steady rate. On the pricing pack it caught a blocking
build failure, an invisible-text defect on the back cover, a legally loaded word in copy meant
to be used verbatim, and two arithmetic errors that had inverted the model's own conclusion.
None of those would have been caught by the committee, because the committee reads
recommendations, not workings. Do not let anyone optimise that stage away for speed.

**The committee needs to be able to say "not now" to a whole workstream.** The most valuable
decision this system can produce is not an approval. It is the committee looking at a
well-researched, well-argued, verified dossier and deciding the programme is better off not
doing that thing in cohort 1 at all. Build that expectation in at the first sitting, or every
dossier will read as a request for permission rather than a decision.
