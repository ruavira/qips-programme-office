# QIPS Workspace Synchronization Register

**Control owner:** Programme Office / W09  
**Applies to:** GitHub, Google Drive, Base44, Supabase, Netlify and Vercel  
**Authority rule:** GitHub is the governed system of record for programme architecture, canon,
workstream state, dossiers, evidence controls and synchronization metadata.

## 1. Purpose

Prevent fragmentation, invisible version drift and false authority across the QIPS Programme
Office's working platforms. This register makes every mirror traceable to an exact Git revision and
makes divergence visible until reconciled.

## 2. Platform roles

| Platform | Permitted role | Prohibited role |
|---|---|---|
| GitHub | Authoritative governed source; canon, state, dossiers, code, schemas, registers and approved source documents | Storing secrets, identifiable participant/patient data or informal decisions without records |
| Google Drive | Human review, comments, editable office copies and signed/minuted records | Becoming canon through comments or silent edits |
| Base44 | Operational interface and projection of repository-governed state | Creating or silently changing canon, decision status or authoritative content |
| Supabase | Approved operational database, audit events and restricted application data after schema/access approval | Acting as programme truth before governance, storing unrestricted sensitive data or overriding GitHub |
| Netlify | Preview or production deployment surface for approved web artifacts | Serving as the only copy of programme content or status |
| Vercel | Preview or production deployment surface for approved applications/services | Serving as the only copy of programme content or status |

## 3. Known environments

| Environment | Identifier / URL | Current governance status |
|---|---|---|
| GitHub repository | `ruavira/qips-programme-office` | AUTHORITATIVE |
| Base44 application | App ID `6a68b8381ea8ff36dd473cd2` | MIRROR — source commit required |
| Base44 live URL | `https://passionate-base-logic-core.base44.app/` | MIRROR — publication claims remain gated |
| Google Drive | URLs registered in `documents/register.yaml` | REVIEW LAYER |
| Supabase | Project identifier not registered in this repository | NOT YET REGISTERED |
| Netlify | Site/deployment identifier not registered in this repository | NOT YET REGISTERED |
| Vercel | Project/deployment identifier not registered in this repository | NOT YET REGISTERED |

## 4. Mandatory synchronization record

Every governed mirror or deployment must record:

- platform;
- environment/project identifier;
- repository source path(s);
- source branch;
- source commit SHA;
- synchronization date and time;
- synchronization actor;
- target revision/deployment identifier;
- validation performed;
- divergence status;
- unresolved differences and owner;
- publication status.

A URL without an exact source commit is not considered synchronized.

## 5. Divergence statuses

- **IN_SYNC** — target was verified against the recorded Git revision.
- **REVIEW_BRANCH_SYNC** — target intentionally reflects an unmerged branch and is visibly labelled.
- **SYNC_PENDING** — repository changed and downstream update has not yet been performed.
- **DRIFT_OPEN** — target differs materially from GitHub and reconciliation is assigned.
- **AUTHORITY_CONFLICT** — two surfaces claim different approved truths; external publication stops.
- **DECOMMISSIONED** — surface is no longer active and redirects/archives are recorded.

`DRIFT_OPEN` or `AUTHORITY_CONFLICT` blocks production publication for the affected artifact.

## 6. Current W02 synchronization baseline

| Surface | Repository source | Source revision | Status | Required action |
|---|---|---|---|---|
| GitHub branch | W02 state, W03 state, CCC charter/docket, W02 dossier, run-002 plan and this register | `agent/w02-governance-synchronization` | REVIEW_BRANCH_SYNC | Merge only after PR validation/review |
| Base44 | W02 status, dependencies, dossier state and links | Pending branch/merge commit | SYNC_PENDING | Mirror after PR is approved or label explicitly as review-branch data |
| Google Drive | Human review copy of W02 decision and operationalization pack | Pending approved source revision | SYNC_PENDING | Create/update review copy and register exact source commit |
| Supabase | No W02 operational schema approved | — | NOT_REGISTERED | Do not create authoritative W02 records until data model and access policy are approved |
| Netlify | No W02 deployment registered | — | NOT_REGISTERED | Deploy only approved web artifacts with source commit metadata |
| Vercel | No W02 deployment registered | — | NOT_REGISTERED | Deploy only approved app/service artifacts with source commit metadata |

## 7. Change protocol

1. Change is proposed and reviewed in GitHub.
2. Repository checks pass and the pull request records governance impact.
3. A merge commit becomes the source revision, unless an explicitly labelled review-branch sync is
   required.
4. Drive/Base44/Supabase/deployment surfaces are updated from that revision.
5. Each target is read back or tested.
6. This register or a machine-readable companion records the target revision and validation.
7. Any divergence is opened as a tracked defect; it is never silently accepted.

## 8. Anti-drift controls

- No approved decision exists only in chat, email, Drive comments or a platform database.
- No mirror may strip the words DRAFT, PROPOSED, PROTOTYPE or PUBLICATION PROHIBITED.
- All generated views declare that they are views and identify their source.
- A downstream write must never be used to overwrite a newer GitHub revision.
- Human-readable and machine-readable status must use the same controlled vocabulary.
- Deployment builds expose source commit metadata in an administrative view or release record.
- Status changes are multidimensional where needed; one coarse label must not conceal prototype,
  publication, decision or dependency state.
- Periodic reconciliation compares GitHub against every registered live surface.

## 9. Reconciliation checklist

For each release or governance wave confirm:

- exact repository commit identified;
- generated files rebuilt;
- YAML/schema checks passed;
- Base44 state read back;
- Drive document title/version/readback checked;
- Supabase migration and row-level-security status checked, when applicable;
- Netlify/Vercel deployment tied to source revision, when applicable;
- links resolve;
- no secret or personal data exposed;
- publication claims match approved canon;
- open drift items have owner and due date.

## 10. Decision rule

When surfaces disagree, GitHub governs unless a signed CCC decision exists that has not yet been
transcribed. In that exceptional case, publication pauses while the signed decision is committed,
the canon/state is regenerated and every mirror is reconciled.
