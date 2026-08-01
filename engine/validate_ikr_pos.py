#!/usr/bin/env python3
"""Validate the QIPS IKR-POS governance profile and core repository registers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "AGENTS.md",
    "governance/ikr-pos/README.md",
    "governance/ikr-pos/repository-charter.md",
    "governance/ikr-pos/installation-manifest.yaml",
    "governance/ikr-pos/system-of-record-map.yaml",
    "governance/ikr-pos/registers/artifacts.yaml",
    "governance/ikr-pos/registers/decisions.yaml",
    "governance/ikr-pos/registers/changes.yaml",
    "governance/ikr-pos/registers/releases.yaml",
    "governance/ikr-pos/registers/access-confidentiality.yaml",
    "governance/ikr-pos/registers/migration-log.yaml",
    "governance/ikr-pos/registers/repository-health.yaml",
    "governance/ikr-pos/portable-export-manifest.yaml",
    "canon/facts.yaml",
    "canon/open-questions.yaml",
    "documents/register.yaml",
    "docs/workspace-synchronization-register.md",
]

YAML_PATHS = [
    path
    for path in REQUIRED_PATHS
    if path.endswith((".yaml", ".yml"))
]


def fail(message: str) -> None:
    print(f"IKR-POS validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(relative_path: str) -> Any:
    path = ROOT / relative_path
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        fail(f"cannot parse {relative_path}: {exc}")


def require_keys(record: dict[str, Any], keys: set[str], context: str) -> None:
    missing = sorted(key for key in keys if key not in record)
    if missing:
        fail(f"{context} is missing keys: {', '.join(missing)}")


def require_unique(records: list[dict[str, Any]], key: str, context: str) -> None:
    values = [record.get(key) for record in records]
    if any(value in (None, "") for value in values):
        fail(f"{context} contains an empty {key}")
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        fail(f"{context} contains duplicate {key} values: {duplicates}")


def validate_required_paths() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        fail(f"required paths are missing: {', '.join(missing)}")


def validate_manifest() -> None:
    data = load_yaml("governance/ikr-pos/installation-manifest.yaml")
    profile = data.get("profile", {})
    require_keys(
        profile,
        {"id", "title", "version", "status", "control_owner", "approval_authority"},
        "installation manifest profile",
    )
    if profile["id"] != "QIPS-IKR-POS":
        fail("installation manifest profile id must be QIPS-IKR-POS")
    assertions = data.get("installation_assertions", {})
    if assertions.get("github_is_authoritative") is not True:
        fail("installation manifest must assert GitHub authority")
    if assertions.get("restricted_data_migrated_to_github") is not False:
        fail("restricted data migration assertion must remain false")


def validate_system_map() -> int:
    data = load_yaml("governance/ikr-pos/system-of-record-map.yaml")
    systems = data.get("systems", [])
    if not isinstance(systems, list) or not systems:
        fail("system-of-record map contains no systems")
    require_unique(systems, "id", "system-of-record map")
    github = next((system for system in systems if system.get("id") == "SYS-GITHUB"), None)
    if not github:
        fail("system-of-record map is missing SYS-GITHUB")
    if github.get("role") != "AUTHORITATIVE_GOVERNED_SYSTEM_OF_RECORD":
        fail("SYS-GITHUB must be authoritative")
    return len(systems)


def validate_artifacts() -> int:
    data = load_yaml("governance/ikr-pos/registers/artifacts.yaml")
    artifacts = data.get("artifacts", [])
    require_unique(artifacts, "id", "artifact register")
    required = {
        "id",
        "title",
        "owner",
        "version",
        "lifecycle_status",
        "authority_class",
        "canonical_location",
        "confidentiality",
        "source_or_parent",
        "review_requirement",
    }
    for artifact in artifacts:
        require_keys(artifact, required, f"artifact {artifact.get('id')}")
        location = artifact["canonical_location"]
        if isinstance(location, str) and not (ROOT / location).exists():
            fail(f"artifact {artifact['id']} points to missing path {location}")
    return len(artifacts)


def validate_decisions() -> int:
    data = load_yaml("governance/ikr-pos/registers/decisions.yaml")
    decisions = data.get("decisions", [])
    require_unique(decisions, "id", "IKR-POS decision register")
    ratification = next((item for item in decisions if item.get("id") == "IKR-D001"), None)
    if not ratification or ratification.get("status") != "PENDING":
        fail("IKR-D001 must exist and remain PENDING until a minuted CCC verdict")
    return len(decisions)


def validate_changes() -> int:
    data = load_yaml("governance/ikr-pos/registers/changes.yaml")
    changes = data.get("changes", [])
    require_unique(changes, "id", "change-control register")
    if not any(item.get("id") == "IKR-CR-001" for item in changes):
        fail("change-control register is missing IKR-CR-001")
    return len(changes)


def validate_documents() -> int:
    data = load_yaml("documents/register.yaml")
    documents = data.get("documents", [])
    require_unique(documents, "id", "document register")
    required = {"id", "title", "owner", "status", "version"}
    for document in documents:
        require_keys(document, required, f"document {document.get('id')}")
    return len(documents)


def validate_facts() -> int:
    data = load_yaml("canon/facts.yaml")
    facts = data.get("facts", [])
    require_unique(facts, "id", "fact registry")
    allowed = {"APPROVED", "PROPOSED", "SUPERSEDED"}
    invalid = [fact.get("id") for fact in facts if fact.get("status") not in allowed]
    if invalid:
        fail(f"fact registry contains invalid statuses: {invalid}")
    return len(facts)


def validate_questions() -> int:
    data = load_yaml("canon/open-questions.yaml")
    questions = data.get("questions", [])
    require_unique(questions, "id", "open-question registry")
    return len(questions)


def main() -> None:
    validate_required_paths()
    for path in YAML_PATHS:
        load_yaml(path)

    validate_manifest()
    counts = {
        "systems": validate_system_map(),
        "artifacts": validate_artifacts(),
        "decisions": validate_decisions(),
        "changes": validate_changes(),
        "documents": validate_documents(),
        "facts": validate_facts(),
        "questions": validate_questions(),
    }

    summary = ", ".join(f"{key}={value}" for key, value in counts.items())
    print(f"IKR-POS validation passed: {summary}")


if __name__ == "__main__":
    main()
