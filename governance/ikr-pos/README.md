# QIPS IKR-POS Profile

**Profile:** QIPS Institutional Knowledge Repository & Project Operating System  
**Profile version:** 1.0.0  
**Installed:** 2026-07-31  
**Control owner:** Programme Office / W09  
**Assurance partner:** W11  
**Approval authority:** Central Coordinating Committee (CCC)

This directory installs IKR-POS as the project-governance operating system for QIPS. It adapts the reusable IKR-POS v1.0.0 skill to QIPS without replacing the existing canon, CCC, workstream, document-register, engine, or control-room architecture.

## Governing order

When instructions conflict, apply this order:

1. signed or minuted CCC decision;
2. `canon/facts.yaml` and other CCC-controlled canon;
3. this QIPS IKR-POS profile and its registers;
4. workstream state, dossiers, plans, and repository operating guidance;
5. Drive review copies, Base44 projections, and other mirrors;
6. chat history, email, working notes, or agent memory.

A downstream mirror never becomes authoritative through polish, recency, or convenience.

## Start here

1. Read [`repository-charter.md`](repository-charter.md).
2. Read [`installation-manifest.yaml`](installation-manifest.yaml).
3. Read [`system-of-record-map.yaml`](system-of-record-map.yaml).
4. Read the relevant register under [`registers/`](registers/).
5. Follow the root [`AGENTS.md`](../../AGENTS.md) before changing project state.
6. Run `python engine/validate_ikr_pos.py` before opening a pull request.

## Installation scope

The installation establishes:

- a repository charter and system-of-record map;
- authority, lifecycle, confidentiality, and change-control rules;
- artifact, decision, change, release, access, migration, and health registers;
- a QIPS-native agent operating contract;
- pull-request and CI controls;
- a non-destructive migration baseline;
- a portable export manifest.

It does **not** authorize any programme fact, W02 prototype, publication, external sharing, deletion, permanent relocation, or production deployment.

## Status

`INSTALLED_PENDING_CCC_RATIFICATION`

The operating controls take effect for repository work immediately after merge as a governance safeguard. Formal policy ratification remains a CCC decision and is recorded in the decision register when minuted.
