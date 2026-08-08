#!/usr/bin/env python3
"""Validate the curriculum spine against canon, and enforce the controlled vocabulary.

Two jobs.

The first is to check that the curriculum design does not silently drift away from the facts the
committee approved. F019 is the interesting one: it publishes "about 4 hours a week in an ordinary
week and about 228 hours in total, DERIVED FROM THE CURRICULUM rather than chosen for marketing."
A derived number that nobody recomputes stops being derived. This recomputes it from the time model
and fails if the design and the published claim have parted company.

The second is the controlled vocabulary. `canon/glossary.md` says the banned terms are "checked for
by the verification stage of every workstream run" — and until now nothing checked. The glossary is
parsed as the source of truth, so adding a row to the table adds a rule; there is no second list to
keep in step.

Usage:
    python3 engine/curriculum.py --self-test
    python3 engine/curriculum.py --time-report
    python3 engine/curriculum.py --vocabulary        # scan published-facing text
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPINE_PATH = ROOT / "engine/schemas/curriculum-spine.yaml"
GLOSSARY_PATH = ROOT / "canon/glossary.md"
FACTS_PATH = ROOT / "canon/facts.yaml"

# Where published-facing language lives. Working notes and evidence dossiers are deliberately
# excluded: they quote regulators and comparators verbatim, and a quotation is not a claim.
VOCABULARY_SCAN_GLOBS = [
    "engine/schemas/*.yaml",
    "outputs/**/*.md",
    "outputs/**/*.html",
]


def load_spine() -> dict[str, Any]:
    return yaml.safe_load(SPINE_PATH.read_text(encoding="utf-8"))


def load_facts() -> dict[str, Any]:
    return {f["id"]: f for f in yaml.safe_load(FACTS_PATH.read_text(encoding="utf-8"))["facts"]}


# ---------------------------------------------------------------------------


def parse_glossary() -> list[tuple[str, list[str]]]:
    """Read canon/glossary.md as the source of truth for banned terms.

    Returns [(permitted_form, [banned_forms])]. Parsing the canon file rather than duplicating it
    means a new row in the table is a new rule, with no second list to fall out of step.
    """
    rules: list[tuple[str, list[str]]] = []
    for line in GLOSSARY_PATH.read_text(encoding="utf-8").split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        use, never = cells[0], cells[1]
        if use.lower() in {"use this", "use"} or set(use) <= set("-: "):
            continue
        banned = [b.strip() for b in never.split(",") if b.strip()]
        if banned:
            rules.append((use, banned))
    return rules


def check_vocabulary(paths: list[Path]) -> list[str]:
    rules = parse_glossary()
    if not rules:
        return ["canon/glossary.md yielded no vocabulary rules; the parser or the file is broken"]

    failures = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(text.split("\n"), start=1):
            stripped = line.strip()
            # A line that is explaining the rule is not breaking it.
            if stripped.startswith("#") or "never this" in stripped.lower():
                continue
            # A line carrying a source URL is a citation. Quoting what somebody else
            # published — an eligibility rule, a regulator's wording, a paper's finding
            # — is not the programme describing itself, and rewriting a quotation to
            # satisfy our own vocabulary would misquote the source.
            #
            # This replaces a far leakier rule that exempted ANY line containing a
            # quote character. In a YAML file nearly every value is quoted, so that
            # exemption silently disabled the check across whole files.
            if "http://" in line or "https://" in line:
                continue

            for permitted, banned_forms in rules:
                for banned in banned_forms:
                    # Plurals matter. The original pattern was \bcourse\b, which does
                    # not match "courses" — nor "students", "modules", "lessons" or
                    # "classes". A vocabulary check that catches only the singular
                    # catches almost nothing, since the plural is the natural form in
                    # marketing copy. Probed and confirmed on 2026-08-02.
                    if re.search(rf"\b{re.escape(banned)}(?:e?s)?\b", line, flags=re.IGNORECASE):
                        failures.append(
                            f"{path.relative_to(ROOT)}:{line_number}: banned term "
                            f"{banned!r} — use {permitted!r}"
                        )
    return failures


# ---------------------------------------------------------------------------


def compute_total_hours(spine: dict[str, Any]) -> dict[str, float]:
    model = spine["time_model"]
    per_month = model["per_month_hours"]
    months = model["months"]
    monthly_total = sum(per_month.values())
    return {
        "per_month": monthly_total,
        "twelve_months": monthly_total * months,
        "observership": model["one_off_hours"]["observership"],
        "grand_total": monthly_total * months + model["one_off_hours"]["observership"],
    }


def check_time_model(spine: dict[str, Any]) -> list[str]:
    """F019: about 4 hours in an ordinary week, about 228 in total, derived from the curriculum."""
    failures = []
    model = spine["time_model"]
    computed = compute_total_hours(spine)
    published = model["published_total_hours"]

    delta = computed["grand_total"] - published
    if abs(delta) > 12:  # one month's worth of drift
        failures.append(
            f"the time model computes {computed['grand_total']:.1f} total hours against a "
            f"published {published} (F019) — a difference of {delta:+.1f}. F019 says the number "
            "is derived from the curriculum, so either the design or the published claim must move."
        )

    # "Ordinary week" means a week in an ordinary month — any month other than the observership
    # month — computed as the monthly total over four weeks. See the ambiguity note in the spine:
    # the phrase admits a narrower reading, and the committee has been asked to settle it.
    per_month = model["per_month_hours"]
    ordinary_week = computed["per_month"] / model["weeks_per_month"]
    published_week = model["published_ordinary_week_hours"]
    if abs(ordinary_week - published_week) > 1.0:
        failures.append(
            f"an ordinary week computes to {ordinary_week:.2f} hours against a published "
            f"{published_week} (F019) — a difference of {ordinary_week - published_week:+.2f}."
        )
    return failures


def check_cycle_integrity(spine: dict[str, Any], facts: dict[str, Any]) -> list[str]:
    """F003: the month is one eLearning release, one live session, one coaching call, one artefact.
    Not three of one and none of another, and not a fifth thing."""
    failures = []
    expected = {"elearning_release", "live_session", "coaching_call", "artefact"}
    got = set(spine["cycle"]["components"])
    if got != expected:
        failures.append(
            f"the monthly cycle is {sorted(got)}; F003 fixes it as {sorted(expected)}. "
            "Any change is a proposed supersession of F003 and must be said so explicitly."
        )
    if spine["cycle"]["artefact_due_days_before_coaching_call"] != 4:
        failures.append("F004 requires artefacts four days before the coaching call")
    return failures


def check_artefact_spine(spine: dict[str, Any]) -> list[str]:
    failures = []
    artefacts = spine["artefacts"]
    if len(artefacts) != 12:
        failures.append(f"the spine has {len(artefacts)} artefacts; Option B requires twelve")
    months = [a["month"] for a in artefacts]
    if months != list(range(1, 13)):
        failures.append(f"artefact months are {months}; expected 1..12 with no gaps or repeats")
    ids = [a["id"] for a in artefacts]
    if len(set(ids)) != len(ids):
        failures.append(f"duplicate artefact ids: {ids}")

    full = [a for a in artefacts if a.get("detail") == "full"]
    if len(full) != 2 or {a["month"] for a in full} != {1, 2}:
        failures.append(
            "exactly months 1 and 2 must be prototyped in full — that is what Item 1 authorised, "
            "and prototyping further would exceed the authorisation"
        )
    for artefact in full:
        for required in ("performance_outcome", "evidence_the_participant_submits",
                         "connects_to_capstone"):
            if not artefact.get(required):
                failures.append(f"{artefact['id']} is marked full but has no {required}")
    return failures


def check_canon_placements(spine: dict[str, Any]) -> list[str]:
    """F010 puts measurement at month 3 and run charts at month 9. F006 puts the observership at
    month 3 to week 2 of month 4. The spine must place its artefacts consistently."""
    failures = []
    by_month = {a["month"]: a for a in spine["artefacts"]}

    m3 = f"{by_month[3]['name']} {by_month[3].get('note', '')}".lower()
    if "measurement" not in m3:
        failures.append("F010 places measurement at month 3; month 3's artefact does not reflect it")
    m9 = f"{by_month[9]['name']} {by_month[9].get('note', '')}".lower()
    if "run chart" not in m9:
        failures.append("F010 places run charts at month 9; month 9's artefact does not reflect it")
    m4 = f"{by_month[4]['name']} {by_month[4].get('note', '')}".lower()
    if "observership" not in m4:
        failures.append("F006 places the observership at month 3 to week 2 of month 4; month 4 does not reflect it")
    return failures


def check_draft_status(spine: dict[str, Any]) -> list[str]:
    """Item 1 condition 1: prototype outputs remain DRAFT and may not be marketed or published."""
    status = spine["spine"]["status"]
    if "DRAFT" not in status.upper():
        return [f"spine status is {status!r}; condition 1 requires DRAFT until the CCC says otherwise"]
    return []


def check_assumptions_recorded(spine: dict[str, Any]) -> list[str]:
    """Item 1 condition 3 requires every prototype to record unresolved assumptions."""
    assumptions = spine.get("unresolved_assumptions", [])
    if not assumptions:
        return ["no unresolved assumptions recorded; condition 3 requires them, and a prototype "
                "with no unresolved assumptions is a prototype that has not been examined"]
    failures = []
    for assumption in assumptions:
        for required in ("assumption", "status", "owner"):
            if not assumption.get(required):
                failures.append(f"{assumption.get('id')} has no {required}")
    return failures


def check_country_adaptation(spine: dict[str, Any]) -> list[str]:
    """Item 1 condition 5 AS AMENDED: built for Nigeria, demonstrating adaptation without building."""
    failures = []
    adaptation = spine.get("country_adaptation", {})
    if adaptation.get("built_for") != "Nigeria":
        failures.append("condition 5 as amended requires the prototype to be built for Nigeria")
    if not adaptation.get("adaptation_points"):
        failures.append("condition 5 as amended requires adaptation points to be demonstrated")
    text = SPINE_PATH.read_text(encoding="utf-8")
    for country in ("Ghana", "Pakistan"):
        if re.search(rf"\bfor {country}\b", text):
            failures.append(
                f"the spine appears to build for {country}; F020 is a PARAMETER and condition 5 "
                "as amended permits demonstration only, not building"
            )
    return failures


# ---------------------------------------------------------------------------


def self_test() -> int:
    print("W02 curriculum spine — validation against canon")
    print()
    spine = load_spine()
    facts = load_facts()

    checks = [
        ("spine is twelve artefacts, months 1-12, months 1-2 full only", lambda: check_artefact_spine(spine)),
        ("monthly cycle matches F003 and F004", lambda: check_cycle_integrity(spine, facts)),
        ("F006 and F010 placements are honoured", lambda: check_canon_placements(spine)),
        ("time model reproduces F019's published hours", lambda: check_time_model(spine)),
        ("prototype is marked DRAFT (condition 1)", lambda: check_draft_status(spine)),
        ("unresolved assumptions recorded (condition 3)", lambda: check_assumptions_recorded(spine)),
        ("country adaptation demonstrated, not built (condition 5 as amended)",
         lambda: check_country_adaptation(spine)),
        ("controlled vocabulary respected in published-facing text",
         lambda: check_vocabulary(sorted(
             p for glob in VOCABULARY_SCAN_GLOBS for p in ROOT.glob(glob)))),
    ]

    failed = 0
    for name, fn in checks:
        try:
            problems = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL  {name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if problems:
            failed += 1
            print(f"  FAIL  {name}", file=sys.stderr)
            for problem in problems[:6]:
                print(f"          {problem}", file=sys.stderr)
            if len(problems) > 6:
                print(f"          ... and {len(problems) - 6} more", file=sys.stderr)
        else:
            print(f"  ok    {name}")

    print()
    if failed:
        print(f"{failed} check(s) failed", file=sys.stderr)
        return 1
    print("All checks passed. The spine is a DRAFT prototype and is not publishable.")
    return 0


def time_report() -> int:
    spine = load_spine()
    model = spine["time_model"]
    computed = compute_total_hours(spine)
    per_month = model["per_month_hours"]

    print("Time model — recomputed from the curriculum, per F019")
    print()
    for name, hours in per_month.items():
        print(f"  {name.replace('_', ' '):<24}{hours:>6.1f} h per month")
    print(f"  {'':<24}{'-' * 6}")
    print(f"  {'per month':<24}{computed['per_month']:>6.1f} h")
    print(f"  {'x 12 months':<24}{computed['twelve_months']:>6.1f} h")
    print(f"  {'observership (F006)':<24}{computed['observership']:>6.1f} h")
    print(f"  {'':<24}{'=' * 6}")
    print(f"  {'TOTAL':<24}{computed['grand_total']:>6.1f} h")
    print(f"  {'published (F019)':<24}{model['published_total_hours']:>6.1f} h")
    print(f"  {'difference':<24}{computed['grand_total'] - model['published_total_hours']:>+6.1f} h")
    print()
    ordinary = computed["per_month"] / model["weeks_per_month"]
    narrow = (per_month["elearning"] + per_month["artefact_production"]) / model["weeks_per_month"]
    print(f"  ordinary week           {ordinary:>6.2f} h   (published {model['published_ordinary_week_hours']})")
    print()
    print("  An ordinary week contains neither the live session, the coaching call, nor")
    print("  observership days. Two of four weeks in a typical month are ordinary.")
    print()
    print(f"  On the NARROWER reading of 'ordinary week' — a week with neither the live")
    print(f"  session nor the coaching call — the figure is {narrow:.2f} h, and the live-session")
    print(f"  week runs to about {narrow + per_month['live_session'] + per_month['coaching_call']:.1f} h.")
    print()
    print("  Weeks are NOT uniform on either reading, and the observership month is heavier")
    print("  again. Marketing that presents 'about 4 hours a week' as a claim about EVERY")
    print("  week is unsupportable.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--time-report", action="store_true")
    parser.add_argument("--vocabulary", action="store_true")
    args = parser.parse_args()
    if args.time_report:
        return time_report()
    if args.vocabulary:
        paths = sorted(p for glob in VOCABULARY_SCAN_GLOBS for p in ROOT.glob(glob))
        problems = check_vocabulary(paths)
        for problem in problems:
            print(problem)
        print(f"\n{len(paths)} file(s) scanned, {len(problems)} finding(s)")
        return 1 if problems else 0
    return self_test()


if __name__ == "__main__":
    raise SystemExit(main())
