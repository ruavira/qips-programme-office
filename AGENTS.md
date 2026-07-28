# Instructions for Claude, Codex, ChatGPT and other agents

## Before doing any work

1. Read `README.md`, `canon/facts.yaml`, `canon/glossary.md`, `canon/open-questions.yaml` and the target workstream's `brief.md` and `state.yaml`.
2. Treat `canon/` as binding governance data, not a drafting area.
3. Check `docs/reconciliation-register.md` before reusing an older artifact.

## Canon rule

A workstream or agent may propose a canon change in a dossier or pull request, but must not quietly rewrite canon. A change to `canon/` requires a recorded CCC verdict and a minute or decision reference. Facts are superseded, never deleted.

Never publish a `PROPOSED` fact. Never fill a visible placeholder with a plausible value. Use `[TO CONFIRM: ...]` until a named source or CCC decision exists.

## Working method

- Work in a branch and use a pull request for review.
- Put research, drafts and dead ends in the owning workstream's `working/` folder.
- Put decision-ready outputs in that workstream's `dossiers/` folder using `engine/schemas/dossier.md`.
- Update the workstream `state.yaml` and `questions.yaml` only when the work performed supports the change.
- Keep the control room generated from repository data. Do not hand-edit it as a source.
- Keep outward-facing language aligned with `canon/glossary.md`.

## Documents and Drive

GitHub stores text-first source content and document metadata. Google Drive stores the human-editable Word/Docs/Sheets review copy. Every Drive document must have an entry in `documents/register.yaml` with an owner, status, version, link and source location. Do not create two unlabeled editable masters.

## Security and privacy

Never commit or echo secrets, tokens, credentials, `.env` files, patient-level data, participant personal data, private contact lists or signed legal documents. Link restricted Drive locations from the register instead. Before every commit or push, scan the staged changes for secrets and `.env` files.

## Verification

Every factual external claim needs a live source URL and accessed date in the owning evidence record. Every decision dossier requires benchmarking, a council verdict and an adversarial verification section before it reaches the CCC.
