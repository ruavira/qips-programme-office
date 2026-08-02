#!/usr/bin/env python3
"""Turn a submitted CCC decision form into a proposed canon change.

The point of this module is that a committee member's answers become the change,
rather than becoming prose that a human then has to translate into YAML. The
translation step is where mistakes happen; this removes it.

What it will never do: write canon. It emits a *proposal* — a patch on a branch
for a human to merge. `AGENTS.md` is unambiguous that only a recorded CCC verdict
writes to canon, and an automated parser is not a verdict.

Usage:
    python3 engine/decision_capture.py --issue-body-file body.md --issue-number 42
    python3 engine/decision_capture.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

VERDICTS = {"PENDING", "APPROVE", "AMEND", "REJECT", "DEFER"}
DECIDED = {"APPROVE", "AMEND", "REJECT", "DEFER"}

# A rejection or deferral without a reason is the one input that breaks the system:
# the reason is what gets written into the workstream brief as a standing constraint,
# and it is how the engine stops re-proposing what the committee already refused.
REASON_REQUIRED = {"REJECT", "DEFER", "AMEND"}


class CaptureError(Exception):
    """A problem with the submitted form that a human must fix."""


def parse_issue_form(body: str) -> dict[str, str]:
    """Parse a GitHub issue-form body into {heading: value}.

    GitHub renders issue forms as `### Label` followed by the value. Empty optional
    fields render as `_No response_`, which we normalise to an empty string.
    """
    fields: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    for line in body.replace("\r\n", "\n").split("\n"):
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            if current is not None:
                fields[current] = "\n".join(buffer).strip()
            current = heading.group(1).strip().lower()
            buffer = []
        elif current is not None:
            buffer.append(line)

    if current is not None:
        fields[current] = "\n".join(buffer).strip()

    for key, value in list(fields.items()):
        if value.strip() in {"_No response_", "_No response_.", ""}:
            fields[key] = ""

    return fields


def load_canon() -> tuple[dict[str, Any], dict[str, Any]]:
    facts = {f["id"]: f for f in yaml.safe_load((ROOT / "canon/facts.yaml").read_text())["facts"]}
    questions = {
        q["id"]: q
        for q in yaml.safe_load((ROOT / "canon/open-questions.yaml").read_text())["questions"]
    }
    return facts, questions


def find_dossier(dossier_id: str) -> Path | None:
    """Locate a dossier by id, e.g. W02-01 -> workstreams/W02/dossiers/W02-01-*.md"""
    if not re.fullmatch(r"W\d{2}-\d{2}", dossier_id):
        return None
    workstream = dossier_id.split("-")[0]
    directory = ROOT / "workstreams" / workstream / "dossiers"
    if not directory.is_dir():
        return None
    matches = sorted(directory.glob(f"{dossier_id}*.md"))
    return matches[0] if matches else None


def check_consistency(record: dict[str, Any], facts: dict[str, Any]) -> list[str]:
    """Check a decision against canon BEFORE it becomes a proposal.

    This is the part that matters. A capture surface without a consistency check
    produces contradictory canon faster than anyone can review it. Every conflict
    class found in a real sitting should be added here.
    """
    problems: list[str] = []

    dossier_id = record["dossier"]
    if not find_dossier(dossier_id):
        problems.append(
            f"Dossier {dossier_id} was not found under workstreams/*/dossiers/. "
            "A verdict cannot be recorded against a dossier that does not exist."
        )

    for fact_id in record["facts_referenced"]:
        if fact_id not in facts:
            problems.append(f"{fact_id} is referenced but does not exist in canon/facts.yaml.")
            continue
        status = facts[fact_id].get("status")
        if status == "SUPERSEDED":
            superseded_by = facts[fact_id].get("superseded_by", "an unrecorded fact")
            problems.append(
                f"{fact_id} is SUPERSEDED by {superseded_by}. A verdict should reference the "
                "current fact, not the superseded one."
            )

    if record["verdict"] in REASON_REQUIRED and not record["reason"]:
        problems.append(
            f"Verdict is {record['verdict']} but no reason was given. The reason is written into "
            "the workstream brief as a standing constraint; without it the engine will re-propose "
            "what the committee already refused."
        )

    return problems


def build_record(fields: dict[str, str], issue_number: int | None) -> dict[str, Any]:
    verdict = (fields.get("ccc verdict") or "").strip().upper()
    if verdict not in VERDICTS:
        raise CaptureError(
            f"CCC verdict must be one of {', '.join(sorted(VERDICTS))}; got {verdict!r}."
        )

    dossier = (fields.get("dossier") or "").strip()
    if not dossier:
        raise CaptureError("Dossier is required.")

    reason = (fields.get("reason for the verdict") or "").strip()
    amendments = (fields.get("amendments") or "").strip()
    body_text = " ".join(fields.values())
    facts_referenced = sorted(set(re.findall(r"\bF\d{3}\b", body_text)))
    questions_referenced = sorted(set(re.findall(r"\bQ\d{3}\b", body_text)))

    return {
        "dossier": dossier,
        "verdict": verdict,
        "reason": reason,
        "amendments": amendments,
        "facts_referenced": facts_referenced,
        "questions_referenced": questions_referenced,
        "captured_from_issue": issue_number,
        "status": "PROPOSED",
        "note": (
            "Captured from a CCC decision form. This is a PROPOSAL. It is not canon and does not "
            "become canon until a human merges the pull request that carries it, and a minute "
            "records the verdict."
        ),
    }


def render_comment(record: dict[str, Any], problems: list[str]) -> str:
    if problems:
        lines = [
            "## Not captured — the form needs a correction",
            "",
            "This verdict was **not** turned into a proposal, because it would not have been "
            "consistent with canon. Nothing has been changed.",
            "",
        ]
        lines += [f"- {p}" for p in problems]
        lines += ["", "Edit the issue and the check will run again."]
        return "\n".join(lines)

    lines = [
        f"## Captured — verdict `{record['verdict']}` on {record['dossier']}",
        "",
        "A proposal branch has been opened. **Nothing is canon yet.** The verdict becomes true "
        "when the pull request is merged and the minute records it.",
        "",
        f"- **Dossier:** {record['dossier']}",
        f"- **Verdict:** {record['verdict']}",
    ]
    if record["facts_referenced"]:
        lines.append(f"- **Facts referenced:** {', '.join(record['facts_referenced'])}")
    if record["questions_referenced"]:
        lines.append(f"- **Questions referenced:** {', '.join(record['questions_referenced'])}")
    if record["reason"]:
        lines += ["", "**Reason recorded:**", "", "> " + record["reason"].replace("\n", "\n> ")]
    if record["amendments"]:
        lines += ["", "**Amendments recorded:**", "", "> " + record["amendments"].replace("\n", "\n> ")]
    return "\n".join(lines)


def run(body: str, issue_number: int | None, out_dir: Path) -> int:
    fields = parse_issue_form(body)
    try:
        record = build_record(fields, issue_number)
    except CaptureError as exc:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "comment.md").write_text(
            f"## Not captured\n\n{exc}\n\nEdit the issue and the check will run again.\n"
        )
        (out_dir / "status.txt").write_text("rejected\n")
        print(f"decision-capture: {exc}", file=sys.stderr)
        return 0  # a bad form is a normal outcome, not a build failure

    if record["verdict"] == "PENDING":
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "status.txt").write_text("pending\n")
        print("decision-capture: verdict is PENDING, nothing to propose")
        return 0

    facts, _ = load_canon()
    problems = check_consistency(record, facts)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "comment.md").write_text(render_comment(record, problems) + "\n")
    (out_dir / "record.yaml").write_text(
        yaml.dump(record, sort_keys=False, default_flow_style=False, width=100, allow_unicode=True)
    )
    (out_dir / "status.txt").write_text(("rejected" if problems else "captured") + "\n")

    if problems:
        print("decision-capture: rejected — " + "; ".join(problems), file=sys.stderr)
    else:
        print(f"decision-capture: captured {record['verdict']} on {record['dossier']}")
    return 0


SELF_TEST_BODY = """### Dossier

W02-01

### Decision requested

Approve the prototype architecture.

### Genuine options and recommendation

Option B recommended.

### Dossier, verification and Drive links

workstreams/W02/dossiers/W02-01-blueprint-architecture.md

### CCC verdict

AMEND

### Reason for the verdict

Condition 5 presumed a three-country set. F020 is a PARAMETER.

### Amendments

Condition 5 rewritten to treat country adaptation as a parameter.
"""


def self_test() -> int:
    failures: list[str] = []

    fields = parse_issue_form(SELF_TEST_BODY)
    if fields.get("dossier") != "W02-01":
        failures.append(f"dossier parsed as {fields.get('dossier')!r}")
    if fields.get("ccc verdict") != "AMEND":
        failures.append(f"verdict parsed as {fields.get('ccc verdict')!r}")

    record = build_record(fields, 1)
    if record["facts_referenced"] != ["F020"]:
        failures.append(f"facts_referenced was {record['facts_referenced']}")

    # A decided verdict with no reason must be refused.
    no_reason = dict(record, reason="")
    facts, _ = load_canon()
    if not check_consistency(no_reason, facts):
        failures.append("a REJECT/AMEND/DEFER with no reason was accepted; it must be refused")

    # An unknown fact must be refused.
    bad_fact = dict(record, facts_referenced=["F999"])
    if not any("F999" in p for p in check_consistency(bad_fact, facts)):
        failures.append("a reference to a non-existent fact was accepted")

    # A nonexistent dossier must be refused.
    bad_dossier = dict(record, dossier="W99-99")
    if not any("W99-99" in p for p in check_consistency(bad_dossier, facts)):
        failures.append("a verdict against a non-existent dossier was accepted")

    # A well-formed verdict must pass.
    if check_consistency(record, facts):
        failures.append(f"a valid record was refused: {check_consistency(record, facts)}")

    # '_No response_' must normalise to empty.
    blank = parse_issue_form("### Reason for the verdict\n\n_No response_\n")
    if blank.get("reason for the verdict") != "":
        failures.append("_No response_ did not normalise to empty")

    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}", file=sys.stderr)
        return 1
    print("decision_capture self-test: all checks passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-body-file")
    parser.add_argument("--issue-number", type=int)
    parser.add_argument("--out-dir", default=".decision-capture")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.issue_body_file:
        parser.error("--issue-body-file is required unless --self-test is given")

    body = Path(args.issue_body_file).read_text(encoding="utf-8")
    return run(body, args.issue_number, Path(args.out_dir))


if __name__ == "__main__":
    raise SystemExit(main())
