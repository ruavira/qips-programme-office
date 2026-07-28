#!/usr/bin/env python3
"""Generate the CCC agenda from repository-governed workstream and dossier state."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ccc" / "agenda.md"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_dossier(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front) or {}, body


def display_date(value) -> str:
    if isinstance(value, date):
        return value.strftime("%-d %B %Y")
    parsed = date.fromisoformat(str(value))
    return parsed.strftime("%-d %B %Y")


def main() -> None:
    dossier_rows = []
    for path in sorted((ROOT / "workstreams").glob("W*/dossiers/*.md")):
        meta, _ = load_dossier(path)
        if meta.get("state_after_submission") != "AWAITING_CCC":
            continue
        dossier_rows.append((meta, path))

    prepared = max((meta.get("prepared") for meta, _ in dossier_rows), default=date.today())
    questions = load_yaml(ROOT / "canon/open-questions.yaml").get("questions", [])
    blocking = [question for question in questions if question.get("blocking")]

    lines = [
        "# CCC agenda — architecture decision sitting",
        "",
        "Generated from workstream state, submitted dossier front matter and",
        "`canon/open-questions.yaml`. This file is a view; do not edit it by hand.",
        "",
        f"**Prepared {display_date(prepared)} · sitting date, chair and quorum to be confirmed.**",
        "",
        "## Item 0 — adopt or confirm the governance",
        "",
        "Before deciding a dossier, confirm the committee's membership, chair, quorum, cadence and",
        "authority under `ccc/charter.md`. Only a minuted CCC verdict may promote a proposed fact into",
        "canon.",
        "",
    ]

    for index, (meta, path) in enumerate(dossier_rows, start=1):
        dossier_id = meta["dossier"]
        workstream = meta["workstream"]
        state = load_yaml(ROOT / "workstreams" / workstream / "state.yaml")
        lines.extend([
            f"## Item {index} — DOSSIER {dossier_id} · {state.get('name', workstream)}",
            "",
            f"**Ready for decision. Verification: {meta.get('verification', 'NOT RUN')}; "
            f"open blocking findings: {meta.get('blocking_findings_open', 'not recorded')}.**",
            "",
            str(meta.get("decision_requested", "Decision request not recorded.")),
            "",
            f"If approved exactly as submitted, this dossier proposes {meta.get('promotes_facts', 0)} "
            "new canon statements. It closes no open question unless the signed verdict explicitly says",
            "otherwise.",
            "",
            f"Repository dossier: `{path.relative_to(ROOT)}`",
            "",
            "**Record:** APPROVE / AMEND / REJECT / DEFER · exact wording · reason or deferral",
            "condition · owner · due date.",
            "",
        ])

    lines.extend([
        f"## Item {len(dossier_rows) + 1} — blocking questions that remain open",
        "",
        "The architecture decisions above may narrow these questions but do not close them by",
        "implication.",
        "",
        "| Q | Question | Owner | Due | Gates |",
        "|---|---|---|---|---|",
    ])
    for question in blocking:
        gates = ", ".join(question.get("blocks", []))
        lines.append(
            f"| {question['id']} | {question['question']} | {question['owner']} | "
            f"{question.get('due', '—')} | {gates or '—'} |"
        )

    lines.extend([
        "",
        f"## Item {len(dossier_rows) + 2} — capacity and next cycle",
        "",
        f"There are {len(dossier_rows)} dossiers in this sitting, which meets the charter's maximum of",
        "three. Do not activate more than three research workstreams in the next cycle. The proposed",
        "next wave is W13 public identity and naming, W14 concept note and collateral, and W16 pricing",
        "and cohort economics; their outputs remain constrained by the verdicts and open questions above.",
        "",
        "## Canon promotion control",
        "",
        "After signed minutes, create one decision record per dossier, promote only the exact approved",
        "wording, update open questions and workstream states, regenerate this agenda and the control-room",
        "export, and record the GitHub revision. No comment in Google Drive or Base44 becomes canon on its",
        "own.",
        "",
    ])

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
