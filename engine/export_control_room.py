#!/usr/bin/env python3
"""Export repository-governed programme state for any control-room frontend."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from workstreams import WORKSTREAMS  # noqa: E402

STATE_TO_STATUS = {
    "DORMANT": "not_started",
    "SCOUTING": "in_discovery",
    "RESEARCHING": "in_discovery",
    "IN_COUNCIL": "in_review",
    "VERIFYING": "in_review",
    "AWAITING_CCC": "decision_required",
    "APPROVED": "approved",
    "BLOCKED": "blocked",
    "DEFERRED": "blocked",
}
STATE_TO_PROGRESS = {
    "DORMANT": 0,
    "SCOUTING": 10,
    "RESEARCHING": 30,
    "IN_COUNCIL": 60,
    "VERIFYING": 75,
    "AWAITING_CCC": 90,
    "APPROVED": 100,
    "BLOCKED": 20,
    "DEFERRED": 20,
}
CLUSTERS = {
    **{f"W{i:02d}": "Evidence & Design" for i in range(1, 5)},
    **{f"W{i:02d}": "Delivery & Faculty" for i in range(5, 7)},
    **{f"W{i:02d}": "Learner & Operations" for i in range(7, 11)},
    **{f"W{i:02d}": "Quality & Data" for i in range(11, 13)},
    **{f"W{i:02d}": "Brand & Market" for i in range(13, 15)},
    **{f"W{i:02d}": "Partnerships & Governance" for i in range(15, 18)},
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def dossiers():
    rows = []
    for path in sorted((ROOT / "workstreams").glob("W*/dossiers/*.md")):
        if path.name == ".keep":
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^dossier:\s*(\S+)", text, re.MULTILINE)
        dossier_id = match.group(1) if match else path.stem
        rows.append({
            "dossier_id": dossier_id,
            "workstream": path.parts[-3],
            "path": str(path.relative_to(ROOT)),
            "status": "awaiting_ccc" if "AWAITING_CCC" in text else "working",
        })
    return rows


def build_snapshot():
    questions = load_yaml(ROOT / "canon/open-questions.yaml").get("questions", [])
    question_ids_by_owner = {}
    for question in questions:
        if question.get("gates"):
            question_ids_by_owner.setdefault(question["owner"], []).append(question["id"])

    workstream_rows = []
    for definition in WORKSTREAMS:
        code = definition["id"]
        state = load_yaml(ROOT / f"workstreams/{code}/state.yaml")
        machine_state = state.get("state", "DORMANT")
        gating_questions = question_ids_by_owner.get(code, [])
        if machine_state == "BLOCKED":
            health = "blocked"
        elif gating_questions or state.get("blocked_by"):
            health = "attention"
        else:
            health = "on_track"
        cohort = {"NOW": "cohort_1", "NEXT": "cohort_2", "LATER": "later"}[state.get("cohort1_scope", definition["cohort1"])]
        workstream_rows.append({
            "code": code,
            "title": definition["name"],
            "directorate": definition["d"],
            "cluster": CLUSTERS[code],
            "state": machine_state,
            "status": STATE_TO_STATUS[machine_state],
            "health": health,
            "cohort": cohort,
            "progress": STATE_TO_PROGRESS[machine_state],
            "question": definition["owner_question"],
            "outputs": definition["outputs"],
            "dependencies": definition["depends_on"],
            "gating_questions": gating_questions,
            # Deprecated alias, kept until every downstream mirror confirms it
            # reads gating_questions. Same content, old key.
            "blocking_questions": gating_questions,
        })

    decision_rows = []
    for question in questions:
        gates = question.get("gates") or []
        decision_rows.append({
            "decision_id": question["id"],
            "question": question["question"],
            "owner": question["owner"],
            "status": "open",
            "gates": gates,
            "while_open": question.get("while_open"),
            "decide_by": iso(question.get("decide_by")),
            "note": question.get("note"),
            # Deprecated aliases for downstream mirrors not yet migrated. The
            # canonical fields are gates / while_open / decide_by above.
            "blocking": bool(gates),
            "blocks": gates,
            "due_date": iso(question.get("decide_by")),
        })

    fact_rows = []
    for fact in load_yaml(ROOT / "canon/facts.yaml").get("facts", []):
        fact_rows.append({
            "fact_id": fact["id"],
            "statement": fact["statement"],
            "status": fact["status"],
            "owner": fact["owner"],
            "source": fact.get("source"),
            "established": iso(fact.get("established")),
        })

    document_rows = []
    for document in load_yaml(ROOT / "documents/register.yaml").get("documents", []):
        document_rows.append({
            "document_id": document["id"],
            "title": document["title"],
            "owner": document["owner"],
            "status": document["status"],
            "version": document.get("version"),
            "repository_source": document.get("repository_source"),
            "drive_url": document.get("drive_url"),
        })

    return {
        "meta": {
            "schema_version": "1.0",
            "source_of_truth": "github",
            "programme": "QIPS Programme Office",
            "workstream_count": len(workstream_rows),
        },
        "workstreams": workstream_rows,
        "decisions": decision_rows,
        "facts": fact_rows,
        "documents": document_rows,
        "dossiers": dossiers(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="exports/control-room.v1.json")
    args = parser.parse_args()
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_snapshot(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
