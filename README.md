# QIPS Programme Office

This repository is the shared operating system for the QIPS programme. It is designed so Emmanuel, Dr. Oyewumi, other agreed collaborators, Claude, Codex and ChatGPT can work from the same governed record without depending on one chat account or one AI workspace.

## Start here

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
