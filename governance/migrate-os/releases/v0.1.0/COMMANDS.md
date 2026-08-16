# Command Index

```bash
python -m migrate_os discover SOURCE --out migration/discovery
python -m migrate_os translate SOURCE --out supabase/migrations
python -m migrate_os scaffold SOURCE TARGET
python -m migrate_os transform SOURCE.csv mapping.csv TARGET.csv
python -m migrate_os files SOURCE_FILES --out migration/source-files.json
python -m migrate_os port-stubs SOURCE packages/domain/src/migrated
python -m migrate_os reconcile SOURCE.csv TARGET.csv --key legacy_base44_id
python -m migrate_os parity SOURCE migration/feature_parity.csv
python -m migrate_os gates migration/gate-evidence.json
```

All outputs are reviewable artifacts. None of these commands applies production migrations, changes DNS or deletes the source.
