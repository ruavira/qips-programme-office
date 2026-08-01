# QIPS IKR-POS Installation Handover

**Installation branch:** `agent/install-ikr-pos`  
**Installation profile:** `QIPS-IKR-POS` v1.0.0  
**Installation date:** 2026-07-31  
**Operating owner:** W09  
**Ratification authority:** CCC

## Completed installation work

- Added the QIPS-native IKR-POS profile without moving, renaming, deleting, or silently replacing existing QIPS structures.
- Preserved the existing canon, CCC, workstream, evidence, document, engine, contract, and synchronization architecture.
- Added the repository charter, system-of-record map, installation manifest, portable-export manifest, and governance registers.
- Extended the repository agent contract and pull-request template.
- Added `engine/validate_ikr_pos.py` and made it a mandatory repository-check gate.
- Recorded the initial migration and repository-health baseline.

## Locked decisions and unchanged canon

- GitHub remains the authoritative governed system of record.
- Google Drive remains the human review, signed-record, and restricted-evidence layer.
- Base44 remains a governed operational mirror and may not originate canon or approval.
- Supabase, Netlify, and Vercel remain unregistered for authoritative QIPS use until governed identifiers, schemas, access policies, and deployment records are approved.
- No programme fact or open question was changed by this installation.
- No policy, dossier, workstream output, publication status, or CCC verdict was promoted.

## Human gates

`IKR-D001` remains `PENDING`. The installation may operate as the repository governance baseline after merge, but formal policy ratification, publication, and any change to CCC authority require a minuted CCC decision.

## Validation required before merge

- `python engine/agenda.py`
- `python engine/controlroom.py`
- `python -m py_compile engine/validate_ikr_pos.py`
- `python engine/validate_ikr_pos.py`
- generated-file consistency check
- repository secret and environment-file scan

## Post-merge synchronization

After merge, record the exact merge revision in:

1. Base44 programme-document and governance records;
2. the registered Google Drive programme-office review layer;
3. `governance/ikr-pos/registers/changes.yaml`;
4. `governance/ikr-pos/registers/releases.yaml`;
5. the workspace synchronization register.

## Remaining controlled actions

- Complete a file-level inventory of active workstream working artifacts.
- Audit Drive permissions, duplicates, restricted locations, and orphan files.
- Run and record the first portable export-and-restore test.
- Review the stale W09 workstream state separately; this installation does not silently change it.
- Define and approve any future Supabase structured-data architecture before activation.

## Exact next objective

Obtain and record the CCC verdict for `IKR-D001`, then execute the first repository-health review and portable restore test without expanding the authority of the installed profile beyond the recorded verdict.
