# Instructions for Claude, Codex, ChatGPT and other agents

This repository is governed by the QIPS IKR-POS profile in `governance/ikr-pos/`. Every contributor must preserve the distinction between programme truth, proposed content, working state, evidence, mirrors, and publication.

## Before doing any work

1. Read `README.md`, `canon/facts.yaml`, `canon/glossary.md`, `canon/open-questions.yaml`, `governance/ikr-pos/repository-charter.md`, `governance/ikr-pos/system-of-record-map.yaml`, and the target workstream's `brief.md` and `state.yaml`.
2. Treat `canon/` as binding governance data, not a drafting area.
3. Check `docs/reconciliation-register.md` before reusing an older artifact.
4. Identify the governing source, affected artifact IDs, lifecycle status, authority class, confidentiality class, and required human gate.
5. Create or update the applicable entry in `governance/ikr-pos/registers/changes.yaml` before a material governance, architecture, migration, release, access, or synchronization change.

## Canon rule

A workstream or agent may propose a canon change in a dossier or pull request, but must not quietly rewrite canon. A change to `canon/` requires a recorded CCC verdict and a minute or decision reference. Facts are superseded, never deleted.

Never publish a `PROPOSED` fact. Never fill a visible placeholder with a plausible value. Use `[TO CONFIRM: ...]`, `TBD`, or `null` until a named source or CCC decision exists.

## Working method

- Work in a branch and use a pull request for review.
- Put research, drafts and dead ends in the owning workstream's `working/` folder.
- Put decision-ready outputs in that workstream's `dossiers/` folder using `engine/schemas/dossier.md`.
- Update the workstream `state.yaml` and `questions.yaml` only when the work performed supports the change.
- Keep the control room generated from repository data. Do not hand-edit it as a source.
- Keep outward-facing language aligned with `canon/glossary.md`.
- Preserve provenance, source links, version, owner, lifecycle, authority, confidentiality, and supersession metadata.
- Never silently overwrite approved or reviewed artifacts; version or supersede them.
- Update affected registers, generated views, synchronization records, and handover notes in the same change wave.
- Stop when authoritative sources conflict; record the conflict and route it to the appropriate human authority.

## Human gates

Do not delete, permanently relocate, externally share, publicly publish, change ownership or permissions, classify legal/regulatory status, alter confidentiality policy, merge unresolved authoritative conflicts, or execute an irreversible migration without explicit human authority.

Do not promote `DRAFT`, `PROPOSED`, `DECISION_REQUIRED`, or `READY_FOR_CCC` material to approved, effective, or published status without the required decision.

## Documents, Drive and platform mirrors

GitHub stores text-first source content and document metadata. Google Drive stores the human-editable Docs/Sheets/Word review copy, signed records, and restricted evidence. Every Drive document must have an entry in `documents/register.yaml` with an ID, owner, status, version, link, and source location. Do not create two unlabeled editable masters.

Drive, Base44, Supabase, Netlify, Vercel, and other systems are governed mirrors or service layers. They must not override a newer GitHub revision. Every downstream synchronization or deployment must record the exact Git source commit and its validation result.

## Security and privacy

Never commit or echo secrets, tokens, credentials, `.env` files, patient-level data, participant personal data, private contact lists, signed legal documents, legal advice, or restricted evidence. Link approved restricted Drive or object-storage locations from the appropriate register instead. Before every commit or push, scan staged changes for secrets and `.env` files.

## Pull-request evidence

Every substantive pull request must state:

- purpose and affected workstreams;
- authoritative sources consulted;
- artifact IDs and registers changed;
- whether programme facts or open questions changed;
- CCC or other human-gate requirement;
- lifecycle, authority, and confidentiality impact;
- destructive actions, if any;
- downstream synchronization or deployment impact;
- validation performed;
- unresolved risks, decisions, and next action.

## Verification

Every factual external claim needs a live source URL and accessed date in the owning evidence record. Every decision dossier requires benchmarking, a council verdict, and an adversarial verification section before it reaches the CCC.

Before handoff run:

```bash
python engine/agenda.py
python engine/controlroom.py
python engine/validate_ikr_pos.py
```

Then confirm generated files are committed and the repository secret scan passes.

## How work reaches the repository

There are three lanes. Use the one that matches what you are doing.

**Lane 1 — you can push.** Work on a branch named `proposal/**`, `ccc/**` or `research/**` and push
it. `.github/workflows/proposal.yml` runs the gates, writes the pull-request body from the actual
diff, opens the pull request, and labels it `canon-change` if `canon/` was touched. You do not write
a pull-request body by hand and you do not need the `gh` CLI.

**Lane 2 — you cannot push.** An agent running outside the repository has no credential, and it must
not be given one over a chat channel — this repository's own secret scan exists to catch exactly that
mistake. Produce a patch and a one-command apply script instead, and let a human push the branch.
Lane 1 takes over from there.

Lane 2 has a hard delivery rule, and it is not optional. **Never hand a human a command that has not
been run.** Build the bundle with `engine/bundle.py`, which runs the exact script the human will run
against a fresh clone of this repository with `git push` stubbed, re-runs every gate in that clone,
and refuses to emit a bundle unless all of it passes.

It runs the script **twice**, because people re-run commands and a delivered script must be safe to
re-run. A bundle for a branch that is already published is cut against the **remote tip**, never
against main: `git am` regenerates commits, so a bundle cut from main produces a sibling history and
the push is rejected as non-fast-forward. Cutting from the remote tip makes every update a
fast-forward, so a force push is never needed and is never offered — if the remote is not an ancestor
of the local branch, `bundle.py` refuses to build and prints the rebase command instead. Each script
also carries the tree hash it promises to produce and checks the applied tree against it before
running any gate, so it proves it built what it said rather than assuming so. The bundle carries a `MANIFEST.json` recording
the base commit, the files touched, every gate and its exit code, and the dry-run verdict. **A bundle
whose manifest does not say `dry_run.passed = true` must not be delivered.**

Three delivered commands have failed in this project, and all three failed the same way — an agent
asserted instead of checking. A path under `~/Downloads` that had never been written, because
delivering a file to a chat is not the same as writing it to a disk. Backticks inside a
double-quoted `--body`, so bash performed command substitution and mangled the pull-request text.
A fix script aimed at a branch that had already merged, which would have pushed to a dead ref and
*appeared* to succeed. `engine/bundle.py` statically refuses all three patterns and then proves the
rest by running it. When a new way of breaking a delivered script is found, add it to `SCRIPT_SMELLS`
and add a case to the self-test, so it can never be found the same way twice.

Bundles go stale — a branch merges, a base moves. Re-prove one before re-delivering it with
`python3 engine/bundle.py --verify <bundle-dir>`.

**Lane 3 — a committee decision.** Open an issue with the `CCC decision` form. When a verdict other
than `PENDING` is saved, `.github/workflows/decision-capture.yml` checks it against canon and, if it
is consistent, opens a proposal branch carrying the decision record. The committee's answers become
the change rather than becoming prose someone else has to translate into YAML — the translation step
is where mistakes happen.

None of these lanes writes canon. All of them produce a pull request.

**A caveat worth knowing.** A pull request opened with `GITHUB_TOKEN` does not trigger other
workflows, so `repository-checks.yml` does not run on a pull request that `proposal.yml` created.
That is why `proposal.yml` runs the same gates itself and records the output in the pull-request
body. Do not remove that on the assumption CI covers it.

## Handover minimum

A handover must include:

- current branch and source commit;
- completed work;
- locked decisions and unchanged canon;
- affected artifacts and registers;
- validation results;
- mirrors updated or still pending;
- open questions, risks, and human gates;
- exact next objective.

No critical project state may exist only in chat or agent memory.
