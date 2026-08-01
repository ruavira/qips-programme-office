# QIPS IKR-POS Repository Charter

## 1. Purpose

The QIPS Programme Office is a durable institutional knowledge and project operating system for a multi-country, multi-workstream professional programme. It must remain understandable, auditable, portable, and recoverable across collaborators, AI systems, review tools, databases, and deployment platforms.

## 2. Scope

This charter governs:

- programme canon, open questions, dependencies, decisions, and controlled language;
- all seventeen workstreams and their dossiers, plans, evidence, and state;
- CCC agenda, minutes, decision records, and generated programme views;
- registered Drive documents and review copies;
- Base44 and future application/database mirrors;
- software, schemas, generators, automation, tests, deployment metadata, and releases;
- evidence metadata, restricted evidence locations, archives, and portable exports.

It does not make restricted evidence, participant data, patient data, private contact lists, signed agreements, credentials, legal advice, or commercially sensitive source files suitable for GitHub.

## 3. Governing principles

1. **GitHub-centred authority.** GitHub is the governed system of record for programme architecture, canon, state, controls, and source-controlled deliverables.
2. **Layer separation.** Authoritative sources, controlled project knowledge, structured data, software, evidence objects, and archives remain logically distinct.
3. **Authority/status separation.** Source authority and artifact lifecycle are separate fields.
4. **Non-destructive change.** Approved or reviewed artifacts are versioned or superseded, never silently overwritten.
5. **CCC-controlled truth.** Only a minuted CCC decision may approve or close programme canon and blocking questions.
6. **Mirror discipline.** Drive, Base44, Supabase, Netlify, Vercel, and future systems must record the exact Git source revision.
7. **Provenance before polish.** A polished or recent artifact is not automatically current, authoritative, or approved.
8. **Portable operation.** No critical state may exist only in one chat, account, application, or undocumented database.
9. **Human gates.** Deletion, external sharing, official approval, public publication, legal classification, access-policy change, and irreversible migration require explicit human authority.
10. **Evidence honesty.** Missing facts remain visible unknowns; agents must not fabricate plausible institutional values.

## 4. Logical knowledge layers

| Layer | QIPS implementation | Authority |
|---|---|---|
| Authoritative source library | Registered official sources and evidence metadata; restricted originals remain in approved Drive/object storage | Source-specific |
| Controlled project knowledge | `canon/`, `workstreams/`, `ccc/`, `docs/`, `documents/`, and `governance/` | GitHub / CCC |
| Structured knowledge and platform data | Base44 mirror now; future approved PostgreSQL/Supabase model | Derived mirror |
| Software and automation | `engine/`, `contracts/`, workflows, tests, deployment configuration | GitHub |
| Evidence and object storage | Registered Drive folders and future approved object storage | Restricted evidence layer |
| Archive and preservation | Git history, superseded canon, archived Drive content, release/export packages | Historical, not active truth |

## 5. Roles

- **Repository owner:** Emmanuel / `ruavira`.
- **Governance control owner:** Programme Office / W09.
- **Quality and repository-health assurance:** W11.
- **Legal, privacy, confidentiality, and data-governance assurance:** W17.
- **Workstream owners:** accountable for classification, provenance, state, and handover of their artifacts.
- **CCC:** approves programme truth, policy, material architecture, release, and formal exceptions.
- **Human collaborators:** review and propose changes through governed channels.
- **AI agents:** replaceable contributors that work through branches, exact source citations, registers, validation, and pull requests.

## 6. Required metadata

Every substantive active artifact must have, directly or through its controlling register:

- artifact ID;
- title;
- owner;
- version or revision;
- lifecycle status;
- authority class;
- canonical location;
- source/parent or provenance;
- created or established date where known;
- review or decision requirement;
- confidentiality class;
- supersession relationship where applicable.

Unknown metadata must be `null`, `TBD`, or explicitly unresolved; it must not be invented.

## 7. Authority classes

- `AUTHORITATIVE_SOURCE`
- `OFFICIAL_EXTERNAL_GUIDANCE`
- `EVIDENCE_SUPPORTED`
- `DERIVED`
- `ADAPTED`
- `PROPOSED`
- `APPROVED_PROJECT_CONTENT`
- `QUARANTINED`
- `HISTORICAL`

## 8. Lifecycle statuses

QIPS retains its existing controlled vocabularies. The IKR-POS profile recognises these lifecycle families:

- `DRAFT`
- `DRAFT_FOR_REVIEW`
- `INTERNAL_REVIEW`
- `TECHNICAL_REVIEW`
- `LEGAL_REVIEW`
- `STAKEHOLDER_REVIEW`
- `DECISION_REQUIRED`
- `READY_FOR_CCC`
- `APPROVED`
- `EFFECTIVE`
- `SUPERSEDED`
- `RETIRED`
- `ARCHIVED`
- `QUARANTINED`
- `HISTORICAL_RECONCILIATION_REQUIRED`

Workstream execution states such as `ACTIVE`, `BLOCKED`, `PAUSED`, or `COMPLETE` remain distinct from artifact lifecycle.

## 9. Versioning and naming

- Working artifacts use `0.x`.
- Approval candidates normally use `0.9`.
- First approved releases use `1.0`.
- Backward-compatible revisions use `1.x`.
- Material architecture or policy changes use a new major version.
- Approved files are never overwritten in place unless the platform preserves immutable revision history and the register records the new revision.
- New portable filenames should follow: `QIPS_[ARTIFACT-ID]_[SHORT-TITLE]_v[VERSION]_[STATUS].[ext]`.

Existing repository paths remain valid and are not renamed solely to satisfy this convention.

## 10. Change workflow

1. Identify the governing source and affected artifacts.
2. Create or update the change-register entry.
3. Work on a branch.
4. Preserve status, authority, confidentiality, and provenance labels.
5. Update all affected registers and generated views.
6. Run repository and IKR-POS validation.
7. Open a pull request with governance impact and synchronization impact.
8. Obtain the required review or CCC verdict.
9. Merge to create the authoritative source revision.
10. Reconcile Drive, Base44, database, and deployment mirrors.
11. Record release or synchronization evidence.

## 11. Release and publication gates

A release or public publication requires:

- exact source commit;
- approved claims and programme facts;
- resolved authority conflicts;
- registered artifacts and documents;
- privacy/confidentiality review where applicable;
- successful repository validation;
- mirror/deployment revision metadata;
- release-register entry;
- explicit human authorization.

## 12. Archive and recovery

- Superseded content remains traceable.
- Archives never become active truth without an explicit restoration decision.
- Portable export manifests must identify included and excluded layers.
- Restore tests are recorded in the repository-health register.
- Restricted evidence is referenced, not copied into portable public packages.

## 13. Human gates

Stop and obtain explicit authority before:

- deleting or permanently relocating originals;
- changing ownership, permissions, or external sharing;
- publishing publicly;
- classifying legal/regulatory status;
- approving programme truth;
- changing confidentiality/privacy policy;
- merging unresolved authoritative conflicts;
- performing irreversible data migration;
- deploying a production surface that makes programme claims.

## 14. Exceptions

Exceptions require a recorded owner, reason, scope, expiry/review date, and approval authority. An undocumented exception is not valid.
