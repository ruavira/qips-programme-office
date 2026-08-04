# ITC Network Operations System — MIGRATE-OS Profile

## Source state

- Source platform: Base44
- Canonical application: ITC Network Operations System
- Source status: controlled internal pilot, conditional go
- Latest known-good checkpoint: `6a6e418b1b355086349ce047`
- Source must remain unchanged and recoverable throughout migration

## Structural inventory confirmed

- 74 entity schemas
- 4 backend controllers
- 14 React pages
- 15 routes
- 73 server actions

## Recommended migration mode

**Backend-first strangler migration**

```text
Base44 source freeze and export
→ GitHub canonical repository
→ Supabase schema/Auth/Storage/RLS
→ portable TypeScript workflow services
→ demonstration-data rehearsals
→ temporary interface against Supabase
→ page-by-page Next.js transition
→ parallel acceptance against Base44
→ cutover and rollback rehearsal
→ controlled switch
→ Base44 read-only stabilization period
```

## Immediate Phase 1–3 outputs

1. Independent Base44 source ZIP and checksum
2. Entity-by-entity data export and record-count manifest
3. File/evidence export and hash manifest
4. Connector and environment-variable inventory
5. Complete MIGRATE-OS source discovery
6. Entity and field mapping to PostgreSQL
7. Workflow/action mapping for all 73 server actions
8. Target permission and RLS design
9. Non-production Supabase project and migration branch
10. First vertical slice: Training Site onboarding or Course Readiness

## Human gates preserved

- Supabase/Vercel project creation and billing approval
- Real-data migration authorization
- Production configuration values
- External-user invitations
- Human acceptance
- Domain cutover
- Base44 decommission
