# QIPS IKR-POS Installation Handover

**Installation profile:** `QIPS-IKR-POS` v1.0.0  
**Installation date:** 2026-07-31  
**Installation PR:** #11  
**Installation source revision:** `0c6334d8a48ee5552f155fa92f277f5ba9321f72`  
**Operating owner:** W09  
**Ratification authority:** CCC  
**Mirror reconciliation:** COMPLETE

## Completed installation work

- Added the QIPS-native IKR-POS profile without moving, renaming, deleting, or silently replacing existing QIPS structures.
- Preserved the existing canon, CCC, workstream, evidence, document, engine, contract, and synchronization architecture.
- Added the repository charter, system-of-record map, installation manifest, portable-export manifest, and governance registers.
- Extended the repository agent contract and pull-request template.
- Added `engine/validate_ikr_pos.py` and made it a mandatory repository-check gate.
- Recorded the initial migration and repository-health baseline.
- Passed the CCC agenda and control-room generators, IKR-POS validator, generated-file consistency check, and secret/environment scan.
- Reconciled the installed profile to Base44 and Google Drive and read both mirrors back.
- Registered the Drive ratification pack in `documents/register.yaml`.
- Recorded the full mirror evidence in `governance/ikr-pos/synchronization-record.md`.

## Locked decisions and unchanged canon

- GitHub remains the authoritative governed system of record.
- Google Drive remains the human review, signed-record, and restricted-evidence layer.
- Base44 remains a governed operational mirror and may not originate canon or approval.
- Supabase, Netlify, and Vercel remain unregistered for authoritative QIPS use until governed identifiers, schemas, access policies, and deployment records are approved.
- No programme fact or open question was changed by this installation.
- No policy, dossier, workstream output, publication status, or CCC verdict was promoted.

## Human gate

`IKR-D001` remains `PENDING` and is registered as `ready_for_ccc`. The installation operates as the
current repository governance baseline, but formal policy ratification, publication, any change to
CCC authority, database activation and deployment require their explicit human gates.

## Validation result

GitHub Actions run `30680835572`, job `91317371425`, completed successfully:

- `python engine/agenda.py`: PASS;
- `python engine/controlroom.py`: PASS;
- `python -m py_compile engine/validate_ikr_pos.py`: PASS;
- `python engine/validate_ikr_pos.py`: PASS;
- generated-file consistency: PASS;
- repository secret and environment-file scan: PASS.

## Mirror reconciliation result

### Base44

Application `6a68b8381ea8ff36dd473cd2` contains five IKR-POS programme-document records and decision
dossier `IKR-D001`. The decision-dossier record is `6a6d5fadb7bc3f06457213fb`, references the exact
installation revision and does not imply approval.

### Google Drive

The native Google Doc **QIPS IKR-POS Installation and Ratification Pack** was created in the QIPS
Programme Office folder and read back:

- folder ID: `1e2hs6yuN27dbZPCVcnQzKfE6ezssXdIc`;
- document ID: `1bIkR9rAbtWVJWuKLSjeYllUQPKgxpgFKHUqGQgZVJwM`;
- URL: `https://docs.google.com/document/d/1bIkR9rAbtWVJWuKLSjeYllUQPKgxpgFKHUqGQgZVJwM`.

## Remaining controlled actions

- Obtain and record the CCC verdict for `IKR-D001`.
- Complete a file-level inventory of active workstream working artifacts.
- Audit Drive permissions, duplicates, restricted locations, and orphan files.
- Run and record the first portable export-and-restore test.
- Review the stale W09 workstream state separately; this installation does not silently change it.
- Define and approve any future Supabase structured-data architecture before activation.

## Exact next objective

Place `IKR-D001` on the continuous CCC decision docket and record an `APPROVE`, `AMEND`, `DEFER`, or
`REJECT` verdict. After the verdict, update GitHub, Base44 and the Drive decision record, then execute
the first repository-health review and portable restore test within the authority granted by that
verdict.
