# W09 working paper — portability and data-residency architecture

**Status:** working recommendation, not canon

**Prepared:** 28 July 2026
**Owner:** W09 Technology and Learning Platform

## Decision frame

The Base44 application should remain the current collaboration and presentation layer, while
GitHub remains the governed source of truth. The design must permit the interface to move to an
independently hosted application and database without rewriting programme logic or losing the
decision trail.

## Boundary

| Concern | Current home | Permanent rule |
|---|---|---|
| Canon, workstream state, dossiers and evidence metadata | GitHub | Authoritative and versioned |
| Human-editable review documents | Google Drive | Registered in `documents/register.yaml`; never silently canonical |
| Control-room interaction | Base44 | Replaceable projection of governed records |
| Participant, patient or signed legal data | Not Base44 at this stage | Restricted system selected under W17 and W12 |
| Authentication directory | Base44 for current access | Not treated as the only exportable identity record |

## Portability controls

1. A platform-neutral JSON contract lives in `contracts/control-room-v1.schema.json`.
2. `engine/export_control_room.py` generates a complete snapshot from repository sources.
3. Front-end code calls a single repository interface; screens never call Base44 entities directly.
4. Base44 entity names map to neutral domain objects and may be replaced by an HTTP/PostgreSQL adapter.
5. Files remain in Drive or GitHub and are referenced by verified identifiers.
6. Sensitive programme data is excluded until W17 approves jurisdiction, retention, access and incident controls.

## Data-residency findings

Base44 states that US storage is the default. EU and UK application-data residency are available
on qualifying plans, but storage residency does not guarantee regional processing. Base44 also
states that application users are not copied or exported during a region move. This makes the
Base44 user table unsuitable as the programme's only durable collaborator directory.

Base44 supports CSV exports for application datasets. Its two-way GitHub synchronization is a
permanent connection with constraints on disconnection and pre-connection version history. The
recommended pattern is therefore a dedicated application repository, separate from the governing
`qips-programme-office` repository.

## Migration target

The target is deliberately vendor-neutral: a React/Next.js-compatible front end, an authenticated
API and PostgreSQL hosted in a jurisdiction approved under W17. A future W09 dossier should compare
specific hosting and identity options only after the residency, processing and controller
requirements are approved.

## Sources

- Base44, “Privacy and security,” accessed 28 July 2026: https://docs.base44.com/Community-and-support/Privacy-and-security
- Base44, “GitHub Integration,” accessed 28 July 2026: https://docs.base44.com/developers/app-code/local-development/github
- Base44, “Managing your app data,” accessed 28 July 2026: https://docs.base44.com/Building-your-app/Managing-your-app-data
