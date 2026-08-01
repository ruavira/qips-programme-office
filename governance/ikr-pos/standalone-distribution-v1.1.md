# IKR-POS Standalone Distribution Record — v1.1.0

**Package:** Institutional Knowledge Repository & Project Operating System  
**Package ID:** `IKR-POS`  
**Version:** `1.1.0`  
**Prepared:** 2026-07-31  
**Distribution purpose:** Cross-model transfer and continued hardening in Claude  
**QIPS source revision at handover:** `9692a548f75dc8d43b323603ced447ae21a0cd7e`

## 1. Authority and release status

- The IKR-POS v1.0.0 reusable core remains `APPROVED_FOR_REUSE`.
- Version 1.1.0 is a backward-compatible distribution and portability enhancement.
- The v1.1.0 package is `READY_FOR_TRANSFER` and its package enhancements remain a `RELEASE_CANDIDATE` until separately approved.
- This distribution does not constitute QIPS CCC ratification, public publication, database activation, deployment approval, or a change to programme authority.
- QIPS decision `IKR-D001` remains pending.

## 2. Scope separation

IKR-POS is not a curriculum. It is the reusable governance, provenance, repository, versioning,
synchronisation, validation and handover operating layer.

The current project contexts remain separate:

- **QIPS W02:** QIPS-wide programme curriculum and blueprint architecture.
- **HEFAMAA Surveyor Training, Assessment and Certification Blueprint:** HEFAMAA accreditation-specific curriculum and competence system.
- **IKR-POS:** domain-neutral governance system capable of governing either project without merging their substantive content.

The skill was first packaged during HEFAMAA work, but its reusable core is intentionally domain-neutral.
The QIPS installation is a separate implementation and does not convert the HEFAMAA curriculum into
QIPS content.

## 3. Standalone package contents

The package contains 36 controlled files, including:

- model-neutral `SKILL.md`;
- Claude Code `CLAUDE.md` project memory;
- package `manifest.yaml`;
- Claude Code, Claude web, ChatGPT and Codex adapters;
- current project handover and scope-separation note;
- Claude session-start prompt;
- repository and register templates;
- JSON schemas;
- package validator and unit test;
- QIPS implementation example;
- release changelog, license and checksums.

## 4. Validation

The package completed:

- `python scripts/validate_package.py` — PASS;
- `python -m unittest discover -s tests -p "test_*.py"` — PASS.

**ZIP SHA-256:** `f831d7db0e691a9aff04894d3e9514e1f82e97cf4134adfc41421cd7423c39eb`

## 5. Google Drive distribution

**Release folder ID:** `1e9JX5wmm6i4iO3fVCE_iakKGcbQP2aFv`  
**Release folder:** `https://drive.google.com/drive/folders/1e9JX5wmm6i4iO3fVCE_iakKGcbQP2aFv`

Verified release files:

| File | Drive ID |
|---|---|
| `IKR-POS_v1.1.0_Claude-Ready.zip` | `19FEP3E754VwC-AkBybrFpNBYiZAg-ME_` |
| `SKILL.md` | `1Qz7wzneABQyw30K0z8o3wR5NV2_jPR3P` |
| `CLAUDE.md` | `1rHZqLSPG40oPPrZBxOYZifWIIyU-4wJ7` |
| `manifest.yaml` | `1cbt8DuvT3O28is0A2fVtBVn6ogwqMcIu` |
| `CURRENT_PROJECT_HANDOVER.md` | `1hj1sRt-eJhYd7st7A5CV8KwQLaJUcZDc` |
| `CLAUDE_SESSION_START.md` | `1mYMVvSYp7OoiT3ExxNGeDb4T5z7ENN2h` |
| `SCOPE_SEPARATION.md` | `1MONJF1uRcWmdoQNvAfJ3yE2h5ngZscGH` |

The folder was listed after upload and all seven handoff items were verified present.

## 6. Claude handover path

### Claude Code

1. Download and extract the ZIP.
2. Open a terminal in the extracted package root.
3. Start Claude Code with `claude`.
4. Paste the contents of `prompts/CLAUDE_SESSION_START.md`.
5. Require Claude to reconstruct state before editing and to run the package validator and tests.

### Claude web or Projects

Upload `SKILL.md`, `manifest.yaml`, `CURRENT_PROJECT_HANDOVER.md`, `SCOPE_SEPARATION.md`, and
`CLAUDE_SESSION_START.md`, followed by only the project sources required for the next objective.

## 7. Exact next objective for Claude

Audit and harden IKR-POS v1.1.0 as a standalone, model-neutral, distributable skill. Preserve the
approved v1.0 core; keep QIPS and HEFAMAA project content outside the reusable core; improve schemas,
templates, installation, restore testing and release packaging; validate every change; and produce a
versioned release snapshot plus complete handover without claiming approval or activating any gated
infrastructure.

## 8. Human gates preserved

- approval of v1.1.0 package enhancements;
- QIPS CCC decision `IKR-D001`;
- QIPS W02 prototype authorization;
- public publication;
- database or production activation;
- ownership, permission, confidentiality or legal-status changes.
