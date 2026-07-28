# Shared operating model

## Recommendation

Use a **GitHub-centred programme office with a Google Drive review layer and one generated control-room interface**.

This is a hub-and-spoke model:

1. GitHub holds the programme's structured memory and audit trail.
2. Google Drive gives non-technical collaborators familiar commenting and editing.
3. Floot presents a friendly dashboard generated from GitHub data.
4. Claude, Codex and ChatGPT connect to GitHub under the human owner's account and work through branches and pull requests.

No AI account owns the programme. The human owners own the repository and decide who receives access.

## What lives where

### GitHub — governed truth and production memory

Store canon, open questions, workstream state, decisions, evidence metadata, text-first source content, schemas, scripts and generated dashboard data. Git history answers who changed what and why. Pull requests give Dr. Oyewumi and other reviewers a clear place to comment on a proposed change before it becomes part of the shared record.

### Google Drive — human review and Office documents

Store working `.docx`, native Google Docs, spreadsheets, decks and signed-off review copies. A Drive file is not canonical merely because it is polished. Its status and link must appear in `documents/register.yaml`.

Recommended Drive folders:

- `00 Start Here`
- `01 CCC Review`
- `02 Workstreams`
- `03 Templates and Toolkits`
- `04 Draft Deliverables`
- `05 Approved Deliverables`
- `90 Restricted`
- `99 Archive`

### Floot — the friendly front door

Floot is appropriate for the live control room because it can turn the repository's structured state into a readable, filterable interface for collaborators who do not want to work inside GitHub. Its first version should remain intentionally narrow:

- workstream status, owner and next action;
- blocking questions and due dates;
- CCC agenda and decision queue;
- links to the relevant GitHub dossier and Drive review document;
- visible distinction between APPROVED, PROPOSED and historical content.

Floot must not maintain separate editable copies of canon or workstream state. Writes should become repository pull requests or structured proposals, not silent database changes.

## The collaboration loop

1. A person or agent selects one workstream and creates a branch.
2. Drafts and evidence are added inside that workstream.
3. Human-friendly documents are reviewed in Drive and linked in the document register.
4. A decision-ready dossier is opened as a pull request.
5. Reviewers comment in the pull request or linked Drive document.
6. The CCC records APPROVE, AMEND, REJECT or DEFER.
7. An approved pull request updates canon, state and the generated control room.

## Access model

- Repository owner: Emmanuel / `ruavira`.
- Programme editors: named human collaborators with GitHub access.
- CCC reviewers: write or triage access, depending on whether they will merge changes.
- AI tools: access through each human's GitHub connector or a local clone. Do not create shared API keys for agents.
- Public audience: approved outputs only, published separately from the private operating repository.

Start private. Publish selected deliverables through a separate website or release process after claims and permissions are approved.
