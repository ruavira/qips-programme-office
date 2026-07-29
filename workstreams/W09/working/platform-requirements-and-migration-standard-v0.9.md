# W09 platform requirements and migration standard v0.9

Status: verified working draft; not an LMS or hosting award

## Architecture decision frame

Use four separable surfaces:

1. **Public site:** approved identity, programme information and application entry only.
2. **Learning environment:** monthly releases, submissions, assessment feedback and participant progress.
3. **Live-session service:** governed links, live captions, attendance and recording controls.
4. **Programme office:** GitHub-governed state, Drive review documents and a replaceable control-room projection.

No surface is the only copy of identity, evidence or decisions. Base44 remains the current friendly front door. The existing RCI Moodle estate is the preferred baseline for a controlled fit test, not an automatic selection.

## Mandatory capability gates

| Gate | Minimum acceptance evidence |
|---|---|
| Monthly cycle | One complete sandbox month: release, live link, artefact submission four days before coaching, feedback, resubmission and status export |
| Access | Role matrix for participant, faculty, coach, assessor, programme operator and auditor; least privilege demonstrated |
| Mobile/low bandwidth | Required journey completed on a representative low-cost Android device, throttled network and interrupted connection; downloadable text/audio alternative available |
| Accessibility | Full critical-path WCAG 2.2 AA audit including theme, content, forms, authentication, plug-ins and mobile app; defects owned and retested |
| Reliability | Named service owner, monitoring, support hours, backup schedule and successful restore test |
| Security | Supported versions, HTTPS, multi-factor authentication for privileged roles, patch cadence, security overview, audit log and incident route |
| Data protection | Approved data inventory, purpose, controller/processor roles, location, sub-processors, retention, deletion and subject-rights route |
| Portability | Versioned export of accounts outside the Base44 user table, enrolments, progress, artefact metadata, assessment outcomes and audit evidence in open formats |
| Live delivery | Captions enabled, host/co-host roles tested, dial-in/audio fallback, attendance minimised, recording/transcript purpose separately approved |
| Operations | Named owner and alternate for provisioning, monthly rollover, exceptions, support, reconciliation and closure |

Failure of any protection, accessibility, restore, portability or critical-path gate blocks launch.

## Repository interface

The control-room front end consumes `contracts/control-room-v1.schema.json`. Platform adapters may read Base44 entities, an authenticated API or PostgreSQL, but screens must not encode programme rules in vendor-specific calls. The repository export remains reproducible from `engine/export_control_room.py`.

## Migration minimum

Before permanent migration, produce and test:

- data dictionary and stable identifiers;
- complete account/contact directory outside non-exportable vendor identity tables;
- CSV/JSON export plus attachment manifest and checksums;
- role and permission mapping;
- immutable decision and consent evidence links;
- cut-over, reconciliation, rollback and deletion certificates;
- one rehearsal with record counts, exceptions and owner sign-off.

The target remains vendor-neutral: accessible web interface, authenticated API and PostgreSQL in a jurisdiction approved under W17. No provider or region is selected in this draft.

## Decision still required

- whether RCI Moodle passes the fit test and who controls its tenant;
- permanent identity provider and account-recovery owner;
- application, LMS, recording and analytics data locations;
- retention and data-protection contact under Q009;
- payment/application integration after W07/W16 decisions;
- transcript and recording purpose, access and deletion rule.
