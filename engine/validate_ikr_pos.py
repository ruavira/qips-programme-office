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
    allowed = {"APPROVED", "PROPOSED", "PARAMETER", "SUPERSEDED"}
    invalid = [fact.get("id") for fact in facts if fact.get("status") not in allowed]
    if invalid:
        fail(f"fact registry contains invalid statuses: {invalid}")

    # A PARAMETER is a decision to stay flexible, not an absence of one. It only means
    # anything if it declares the range the design must hold across, and says plainly what
    # it does and does not hold up — otherwise it is a gap wearing a better label.
    required_parameter_keys = {
        "range",
        "design_valid_across_range",
        "why",
        "gates",
        "does_not_gate",
        "decide_by",
    }
    for fact in facts:
        if fact.get("status") != "PARAMETER":
            continue
        parameter = fact.get("parameter")
        if not isinstance(parameter, dict):
            fail(f"{fact.get('id')} is PARAMETER but declares no parameter block")
        missing = sorted(required_parameter_keys - set(parameter))
        if missing:
            fail(f"{fact.get('id')} parameter block is missing keys: {', '.join(missing)}")
        if parameter.get("design_valid_across_range") is not True:
            fail(
                f"{fact.get('id')} is PARAMETER but does not assert the design is valid "
                "across its declared range; resolve it or reclassify it as PROPOSED"
            )
    return len(facts)


def validate_dependency_graph() -> int:
    """The dependency graph must be a DAG. A cycle silently breaks every downstream
    calculation — concurrency planning, unblocking, and the agenda all depend on being
    able to topologically sort it. W02 and W03 were mutually dependent until 2026-08-01,
    which meant the sort halted after one wave and nobody noticed."""
    data = load_yaml("canon/dependencies.yaml")
    graph = {code: list(node.get("depends_on") or []) for code, node in data.get("dependencies", {}).items()}

    for code, deps in graph.items():
        unknown = [d for d in deps if d not in graph]
        if unknown:
            fail(f"{code} depends on unknown workstreams: {', '.join(unknown)}")

    colour: dict[str, int] = {}

    def visit(node: str, trail: list[str]) -> None:
        colour[node] = 1
        for nxt in graph[node]:
            if colour.get(nxt) == 1:
                cycle = trail[trail.index(nxt):] + [nxt] if nxt in trail else [nxt, node, nxt]
                fail(
                    "dependency graph contains a cycle: " + " -> ".join(cycle)
                    + ". Use calibrates_with for a mutual, non-blocking relationship."
                )
            if colour.get(nxt, 0) == 0:
                visit(nxt, trail + [nxt])
        colour[node] = 2

    for code in graph:
        if colour.get(code, 0) == 0:
            visit(code, [code])
    return len(graph)


def validate_narratives() -> int:
    """Every workstream carries a human-readable layer in the repository, so no front end
    is the only place a reviewer's view of the programme exists."""
    required = {"code", "plain_question", "success_looks_like", "waiting_on", "can_proceed_now"}
    codes = sorted((ROOT / "workstreams").iterdir()) if (ROOT / "workstreams").is_dir() else []
    count = 0
    for path in codes:
        if not path.is_dir():
            continue
        narrative = path / "narrative.yaml"
        if not narrative.exists():
            fail(f"{path.name} has no narrative.yaml")
        record = load_yaml(f"workstreams/{path.name}/narrative.yaml")
        require_keys(record, required, f"{path.name} narrative")
        if record.get("code") != path.name:
            fail(f"{path.name}/narrative.yaml declares code {record.get('code')}")
        count += 1
    return count


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
        "graph": validate_dependency_graph(),
        "narratives": validate_narratives(),
    }

    summary = ", ".join(f"{key}={value}" for key, value in counts.items())
    print(f"IKR-POS validation passed: {summary}")


if __name__ == "__main__":
    main()
