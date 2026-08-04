# MIGRATE-OS — Application Migration & Replatforming Operating System

**Version:** `0.1.0`  
**Status:** `RELEASE_CANDIDATE`  
**Prepared:** 2026-08-03

MIGRATE-OS is the technical migration companion to IKR-POS. IKR-POS governs authority, provenance, registers and handover; MIGRATE-OS performs source discovery, schema translation, target scaffolding, data transformation, file manifests, workflow porting, record reconciliation, feature/control parity, cutover, rollback and stabilization.

## First-class migration path

`Base44 → GitHub + Next.js + Supabase`

The core protocol is adapter-based and supports other builder, database, authentication, storage and hosting migrations.

## Executable capabilities

- deterministic Base44 inventory of entities, controllers/actions, pages and routes;
- reviewable Supabase/Postgres DDL generation with preserved legacy IDs;
- Next.js/Supabase target workspace scaffolding;
- explicit CSV transformation mappings;
- source/target record reconciliation;
- file checksum manifests and comparison;
- generated portable TypeScript workflow-service stubs;
- feature-parity validation;
- nine blocking go/no-go gates;
- cutover, rollback and human-acceptance controls.

## Safety posture

The skill is non-destructive. It does not apply generated SQL, change DNS, expose secrets, invite production users, delete the source, or claim human acceptance. Generated security begins deny-by-default and must be reviewed.

## Validation

- Package validator: PASS
- Unit tests: 13/13 PASS
- Command flows exercised: discovery, translation, scaffold, transformation, file manifest, port stubs, reconciliation and parity
- Live ITC structure probe: 74 entities, 4 controllers, 14 pages, 15 routes and 73 server actions

The release is not yet production-proven. It still requires a complete non-production Supabase rehearsal and rollback test against a real Base44 export.
