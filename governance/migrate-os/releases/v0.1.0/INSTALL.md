# Install MIGRATE-OS v0.1.0

1. Obtain `MIGRATE-OS_v0.1.0.zip` and verify SHA-256:

   `24699dfc3ff4196bc7088b0c9729901c542a9d758ac1a7676bd6d3773ad28954`

2. Extract the package into an isolated workspace.
3. Read `SKILL.md`, `manifest.yaml`, `AGENTS.md` and `MIGRATE_OS_HANDOVER.md`.
4. Run:

   ```bash
   python scripts/validate_package.py
   PYTHONPATH=. python -m unittest discover -s tests -p 'test_*.py' -v
   ```

5. For a Base44 migration, place or clone the independent Base44 source export outside the live application and run:

   ```bash
   python -m migrate_os discover /path/to/base44-export --out migration/discovery
   python -m migrate_os translate /path/to/base44-export --out supabase/migrations
   python -m migrate_os port-stubs /path/to/base44-export packages/domain/src/migrated
   ```

6. Do not apply generated SQL, use real data, invite production users, change DNS or decommission the source until the corresponding human gates are approved.
