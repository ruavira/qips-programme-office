# QIPS Programme Office

This repository is the shared operating system for the QIPS programme. It is designed so Emmanuel, Dr. Oyewumi, other agreed collaborators, Claude, Codex and ChatGPT can work from the same governed record without depending on one chat account or one AI workspace.

## Start here

**Taking over this project, as a person or as an agent? Read [`HANDOFF.md`](HANDOFF.md) first.**
It is the current baton: where the work stands, what is decided, what is blocked on a human, the
invariants you must not regress, and how to hand it back. Everything below is still true; the
handoff tells you which parts matter today.

1. Open [`ccc/control-room.html`](ccc/control-room.html) for the whole-programme view.
2. Read [`canon/facts.yaml`](canon/facts.yaml) before treating any statement as settled.
3. Read [`canon/open-questions.yaml`](canon/open-questions.yaml) for the decisions currently blocking progress.
4. Open the relevant `workstreams/W##/` folder before starting work.
5. Submit decisions through a pull request. A workstream may propose a canon change; only a recorded Central Coordinating Committee decision may approve it.

## The simple operating model

- **GitHub is the system of record.** Canon, workstream status, decision dossiers, evidence metadata and generated views live here.
- **Google Drive is the review desk.** Word documents, Google Docs and spreadsheets live there when people need comments, suggestions or familiar editing tools.
- **The control room is a view.** Floot or another friendly web front end may present the repository data, but it never becomes a competing source of truth.
- **AI accounts are replaceable workers.** Claude, Codex and ChatGPT read the same repository, work on branches, and hand back pull requests. No critical state should exist only inside a chat.

The full operating model is in [`docs/operating-model.md`](docs/operating-model.md). Cross-agent access instructions are in [`docs/agent-access.md`](docs/agent-access.md).

## If you are here to decide something

You will ever do three things. Nothing else in this repository is addressed to you.

**Read.** Open [`ccc/control-room.html`](ccc/control-room.html). Every workstream is a card: the
question it exists to answer, what it must produce, what it is waiting on. Dossiers link from the
card. If you would rather read in the repository, they live at a predictable path —
`workstreams/W03/dossiers/W03-01-*.md`.

**Comment.** You do not need to learn git and you should not edit files directly. If you want
something changed, say so in a comment; it is faster and it leaves a record of *why*.

**Decide.** When a dossier is ready it appears in **Issues** with the label `ccc-decision`. The top
half tells you what is being decided, what canon already establishes and what the genuine options
are. The bottom half is yours: **Approve · Amend · Reject · Defer**, a box for your reasoning, and a
box for the condition under which the decision should come back to you automatically.

Two things happen when you save a verdict other than `PENDING`. It is **checked against canon
before it is accepted** — if it cites a fact that has been superseded, or a dossier that does not
exist, or if it is a rejection with no reason, the system refuses it and tells you why rather than
recording something inconsistent. If it passes, a **proposal branch opens carrying your decision**,
so your answer becomes the change rather than becoming prose somebody has to translate into YAML.

Nothing you write becomes canon on its own. It becomes canon when the change is merged and a minute
records it.

One thing matters more than any other: **a rejection must carry a reason.** The reason is written
back into the workstream's brief as a permanent constraint, and that is how the system stops
proposing the thing you already refused. A rejection without a reason is the only input that breaks
this — which is why the check refuses it.

## Repository map

| Location | Purpose |
|---|---|
| `canon/` | Approved and proposed programme facts, controlled language, dependencies and open questions |
| `workstreams/W01`–`W17` | Briefs, working material, state, inbox and decision dossiers for each workstream |
| `ccc/` | Committee charter, agenda, cadence, roadmap, minutes and generated control room |
| `engine/` | Scripts and schemas that generate the workstream scaffold and control room |
| `documents/` | Register linking repository records to human-editable Drive documents |
| `docs/` | Plain-language operating guidance, access instructions and reconciliation notes |

## Current caution

Several earlier artifacts describe a 12–18-month programme, seven gates or thirteen deliverables. Current canon fixes a **12-month** programme; older material must be treated as historical until reconciled. See [`docs/reconciliation-register.md`](docs/reconciliation-register.md).

## Security

This repository is private by default. Do not commit participant data, patient data, credentials, `.env` files, signed agreements, private contact lists or commercially sensitive source files unless the CCC has approved the storage location and access model.
