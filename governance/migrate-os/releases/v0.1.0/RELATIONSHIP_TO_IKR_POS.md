# Relationship to IKR-POS

IKR-POS and MIGRATE-OS are complementary:

| System | Responsibility |
|---|---|
| IKR-POS | Authority, provenance, registers, controlled artifacts, decisions, releases, checksums and handover |
| MIGRATE-OS | Technical discovery, translation, implementation, data migration, parity, cutover, rollback and stabilization |

When both are installed, IKR-POS records the governed state and MIGRATE-OS performs the implementation change. MIGRATE-OS must not bypass IKR-POS decision or release gates, and IKR-POS must not be treated as a substitute for technical migration testing.
