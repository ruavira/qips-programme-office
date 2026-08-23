# Change Request: QIPS cross-platform recovery

**Requester:** Programme director  
**Date:** 2026-08-23  
**Priority:** Critical  
**Status:** Implemented / awaiting owner review of draft PR #28

**Change record:** IKR-CR-006

## Description

Contain unsafe Google Drive and Base44 access paths, restore GitHub-centred mirror discipline,
repair stale governance records, recover the Netlify deployment path, and prepare the next
programme-production wave without promoting unminuted canon.

## Business justification

The current state exposes QIPS Drive material to link-based editing, indexes unrelated Drive
metadata into Base44, presents public claims beyond unresolved gates, and leaves the live design
walkthrough behind the authoritative repository. Recovery reduces confidentiality, integrity,
publication and continuity risk while preserving the existing programme design.

## Impact analysis

| Area | Impact | Details |
|---|---|---|
| Users | Medium | Named collaborators retain access; anonymous link editors lose write access. |
| Systems | High | Drive, Base44, GitHub and Netlify are reconciled to explicit authority boundaries. |
| Processes | High | Base44 becomes a mirror; CCC remains the only canon-approval authority. |
| Cost | Low | No new paid service is authorized; Netlify credentials must already exist or be created by the owner. |

## Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Intended collaborator loses access | Low | High | Preserve all named permissions and verify owner access before and after containment. |
| Base44 cleanup removes useful records | Medium | High | Quarantine rather than delete and checkpoint the application before changes. |
| Public page becomes inconsistent | Medium | Medium | Use canon-safe holding copy and visually verify public and authenticated routes. |
| Canon is accidentally promoted | Low | Critical | Do not edit canon; route F030 and other choices through CCC decision material. |
| New Netlify deployment fails | Medium | Medium | Keep the existing deployment as rollback and verify the exact source revision before acceptance. |

## Implementation plan

| Step | Owner | Timing | Dependencies |
|---|---|---|---|
| Contain Drive link editing | W09/W17 | Immediate | Preserve named permissions |
| Stop whole-Drive Base44 ingestion | W09 | Immediate | Base44 checkpoint |
| Repair governance state and registers | W09/W11 | Next | Containment evidence |
| Reconcile mirrors | W09/W17 | After repository review | Current Git source revision |
| Restore Netlify deployment | W09 | After governance reconciliation | Repository secrets available in GitHub |
| Restart programme production | Workstream owners | After recovery | Open-decision gates remain visible |

## Rollback plan

- **Trigger:** owner access fails, Base44 build fails, public copy contradicts canon, or deployment
  verification cannot identify the intended source revision.
- **Drive:** use the recorded permission inventory to restore the exact prior sharing entry only if
  named access cannot be repaired directly.
- **Base44:** restore the pre-recovery sandbox checkpoint; quarantined records remain recoverable.
- **GitHub:** revert the proposal commit or close the unmerged pull request.
- **Netlify:** keep serving the prior deployment until the new revision passes verification.

## Execution outcome

| Step | Outcome | Receipt |
|---|---|---|
| Drive containment | Complete | General access is Restricted; no anonymous permission remains; owner access was preserved. |
| Base44 containment and correction | Complete | Hardened revision `36514ab` is published, security-clean and visually verified. |
| GitHub governance recovery | Complete / review open | Draft PR #28 is mergeable and unmerged; repository-check run #78 passed at `b774398`. |
| Netlify deployment recovery | Complete | Production deploy `6a8b603c0407f60ee8ea46f8` is published from source `2b17389`. |
| Live walkthrough assurance | Pass | Desktop/mobile layout, decision navigation, PWA assets and browser console passed; stale revision `0dd9c5e` is absent. |
| Netlify form continuity | Pass | Form detection is enabled; `qips-walkthrough-responses` is active and its two historical submissions remain. No test response was sent. |

No programme fact or open question was approved, closed or superseded by this recovery.

## Approvals

| Approver | Role | Status |
|---|---|---|
| Programme director | Access, synchronization, presentation and deployment recovery | Approved 2026-08-23 |
| CCC | Programme canon and formal policy decisions | Not delegated; required where applicable |

