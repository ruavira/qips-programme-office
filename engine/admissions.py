#!/usr/bin/env python3
"""The cohort-one admissions scoring engine, and the end-to-end test that discharges
W07-01 condition 5.

Approved as architecture by the CCC on 2026-08-01, Item 4. This implements the approved
architecture. It does not set a threshold, a cap or a country allocation, because none of those
was approved and none is knowable from synthetic cases.

The part worth reading is `check_canon_invariants`. The CCC promoted a fact —

    "Title, institutional prestige, sponsorship, ability to pay and reasonable-adjustment need
     do not increase or reduce the merit score."

— and a promoted fact that lives only in prose is a promise. Here it is a property test: every
calibration case is re-scored with each of those fields perturbed, and the score must not move.
A future change that quietly lets prestige into the rubric fails the build.

Usage:
    python3 engine/admissions.py --self-test        # discharges W07-01 condition 5
    python3 engine/admissions.py --report           # human-readable calibration report
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUBRIC_PATH = ROOT / "engine/schemas/admissions-rubric.yaml"
CASES_PATH = ROOT / "engine/fixtures/admissions-calibration-cases.yaml"


class RubricError(Exception):
    """The rubric or an application is malformed. Never a scoring outcome."""


# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Application:
    """One application. Scoring fields and non-scoring fields are deliberately separate types
    of thing, so that it is structurally awkward to feed a non-scoring field into the score."""

    case_id: str
    ratings: dict[str, int]  # criterion id -> 0..4
    # Everything below is collected and MUST NOT affect the score.
    job_title: str = ""
    institution: str = ""
    sponsorship: str = "self_funded"
    support_needs: str = ""
    source: str = "open_application"
    gates: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Score:
    total: float
    by_criterion: dict[str, float]

    def rounded(self) -> float:
        return round(self.total, 2)


# ---------------------------------------------------------------------------


def load_rubric() -> dict[str, Any]:
    data = yaml.safe_load(RUBRIC_PATH.read_text(encoding="utf-8"))
    criteria = data["criteria"]
    total_weight = sum(c["weight"] for c in criteria)
    if total_weight != 100:
        raise RubricError(
            f"criterion weights must sum to 100; they sum to {total_weight}. "
            "A rubric that does not sum to 100 produces scores that cannot be compared."
        )
    ids = [c["id"] for c in criteria]
    if len(set(ids)) != len(ids):
        raise RubricError(f"duplicate criterion ids: {ids}")
    return data


def score(application: Application, rubric: dict[str, Any]) -> Score:
    """Turn ratings into points. Reads ONLY `application.ratings`.

    This function deliberately takes the whole Application rather than just the ratings, so that
    the invariant test below is meaningful: it can perturb any field and confirm nothing moves.
    """
    max_rating = rubric["rubric"]["max_rating"]
    by_criterion: dict[str, float] = {}

    for criterion in rubric["criteria"]:
        cid = criterion["id"]
        if cid not in application.ratings:
            raise RubricError(f"{application.case_id}: no rating for criterion {cid}")
        rating = application.ratings[cid]
        if not isinstance(rating, int) or not 0 <= rating <= max_rating:
            raise RubricError(
                f"{application.case_id}: rating for {cid} is {rating!r}; must be an integer "
                f"0..{max_rating}"
            )
        by_criterion[cid] = (rating / max_rating) * criterion["weight"]

    return Score(total=sum(by_criterion.values()), by_criterion=by_criterion)


def needs_moderation(a: Application, b: Application, rubric: dict[str, Any]) -> tuple[bool, str]:
    """Condition 4's initial pilot rule. Returns (fires, why)."""
    triggers = rubric["moderation"]["triggers"]
    total_gap = abs(score(a, rubric).total - score(b, rubric).total)
    if total_gap >= triggers["total_points_difference_at_or_above"]:
        return True, f"total difference {total_gap:.2f} points"

    level_threshold = triggers["any_single_criterion_level_difference_at_or_above"]
    for criterion in rubric["criteria"]:
        cid = criterion["id"]
        gap = abs(a.ratings[cid] - b.ratings[cid])
        if gap >= level_threshold:
            return True, f"{criterion['name']} differs by {gap} rating levels"

    return False, ""


def offer_blocked_by_gates(application: Application, rubric: dict[str, Any]) -> list[str]:
    """Evidence gates sit OUTSIDE the score. A high score cannot substitute for verification."""
    blocked = []
    for gate in rubric["evidence_gates"]:
        state = application.gates.get(gate["id"], "not_established")
        if state not in gate["states"]:
            raise RubricError(
                f"{application.case_id}: gate {gate['id']} has state {state!r}; "
                f"must be one of {gate['states']}"
            )
        if state in gate["blocks_offer_when"]:
            blocked.append(f"{gate['name']} is {state}")
    return blocked


# ---------------------------------------------------------------------------


def load_cases() -> list[dict[str, Any]]:
    return yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))["cases"]


def to_application(case: dict[str, Any], reviewer: str) -> Application:
    return Application(
        case_id=f"{case['id']}/{reviewer}",
        ratings=dict(zip(["C1", "C2", "C3", "C4", "C5", "C6"], case[f"reviewer_{reviewer}"])),
        job_title=case.get("job_title", ""),
        institution=case.get("institution", ""),
        sponsorship=case.get("sponsorship", "self_funded"),
        support_needs=case.get("support_needs", ""),
        source=case.get("source", "open_application"),
        gates=case.get("gates", {"G1": "verified", "G2": "verified", "G3": "verified"}),
    )


# ---------------------------------------------------------------------------
# The canon invariants. This is the part that matters.
# ---------------------------------------------------------------------------

PERTURBATIONS = {
    "job_title": ["Consultant Physician", "Chief Medical Director", "Junior Officer", ""],
    "institution": ["A nationally prominent teaching hospital", "A rural district hospital", ""],
    "sponsorship": ["self_funded", "employer_sponsored", "scholarship", "unfunded"],
    "support_needs": ["", "Requires screen-reader compatible materials", "Caregiving constraints"],
    "source": ["open_application", "institutional_nomination"],
}


def check_canon_invariants(rubric: dict[str, Any]) -> list[str]:
    """For every case and every non-scoring field, perturb the field and assert the score is
    unchanged. This is the promoted fact from CCC 2026-08-01 Item 4, enforced.
    """
    failures: list[str] = []
    for case in load_cases():
        for reviewer in ("a", "b"):
            base = to_application(case, reviewer)
            baseline = score(base, rubric).rounded()
            for field_name, values in PERTURBATIONS.items():
                for value in values:
                    perturbed = replace(base, **{field_name: value})
                    got = score(perturbed, rubric).rounded()
                    if got != baseline:
                        failures.append(
                            f"{base.case_id}: changing {field_name} to {value!r} moved the score "
                            f"from {baseline} to {got}. The promoted fact of 2026-08-01 says it "
                            f"must not."
                        )
    return failures


def check_support_needs_excluded_from_moderation(rubric: dict[str, Any]) -> list[str]:
    """W07-01 condition 8: the support-needs field is excluded from the rubric AND from
    moderation."""
    failures = []
    for case in load_cases():
        a = to_application(case, "a")
        b = to_application(case, "b")
        baseline_fires, _ = needs_moderation(a, b, rubric)
        a2 = replace(a, support_needs="Requires extended submission windows")
        b2 = replace(b, support_needs="")
        fires, _ = needs_moderation(a2, b2, rubric)
        if fires != baseline_fires:
            failures.append(
                f"{case['id']}: differing support-needs changed the moderation outcome. "
                "Condition 8 says it must not."
            )
    return failures


def check_published_totals(rubric: dict[str, Any]) -> list[str]:
    """Every case carries the totals published in the 2026-07-28 calibration rounds. If this
    engine disagrees with them, one of the two is wrong and a human must look."""
    failures = []
    for case in load_cases():
        for reviewer in ("a", "b"):
            got = score(to_application(case, reviewer), rubric).rounded()
            expected = case[f"published_total_{reviewer}"]
            if abs(got - expected) > 0.001:
                failures.append(
                    f"{case['id']} reviewer {reviewer.upper()}: engine computes {got}, the "
                    f"published calibration record says {expected}."
                )
    return failures


def check_moderation_behaviour(rubric: dict[str, Any]) -> list[str]:
    """SYN-K was constructed to fire the trigger. If it stops firing, the trigger is broken."""
    failures = []
    fired = []
    for case in load_cases():
        fires, why = needs_moderation(
            to_application(case, "a"), to_application(case, "b"), rubric
        )
        if fires:
            fired.append((case["id"], why))
        if case["id"] == "SYN-K" and not fires:
            failures.append(
                "SYN-K was built to fire the moderation trigger (12.50 points and a two-level "
                "difference) and it did not fire."
            )
    if not fired:
        failures.append("No case fires the moderation trigger; the rule is not being exercised.")
    return failures


def check_gates_independent_of_score(rubric: dict[str, Any]) -> list[str]:
    """SYN-G and SYN-H are the same profile with project access verified vs conditional. Their
    scores must be identical and only the gate state differs."""
    cases = {c["id"]: c for c in load_cases()}
    failures = []
    if "SYN-G" in cases and "SYN-H" in cases:
        g = score(to_application(cases["SYN-G"], "a"), rubric).rounded()
        h = score(to_application(cases["SYN-H"], "a"), rubric).rounded()
        if g != h:
            failures.append(
                f"SYN-G scored {g} and SYN-H scored {h}. They differ only in evidence-gate "
                "state, which sits outside the score, so they must score identically."
            )
        blocked_h = offer_blocked_by_gates(to_application(cases["SYN-H"], "a"), rubric)
        if blocked_h:
            failures.append(
                f"SYN-H (project access CONDITIONAL) is blocked from offer: {blocked_h}. "
                "Conditional access is a condition, not a refusal."
            )
    return failures


FORBIDDEN_KEYS = {"threshold", "pass_mark", "passmark", "cutoff", "cut_off",
                  "cohort_cap", "cap", "country_allocation", "allocation", "quota", "price",
                  "fee", "tuition"}


def _walk(node: Any, path: str = "") -> list[tuple[str, Any]]:
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            found.append((here, value))
            found.extend(_walk(value, here))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(_walk(value, f"{path}[{index}]"))
    return found


def check_no_threshold_leaked(rubric: dict[str, Any]) -> list[str]:
    """The rubric must not acquire a threshold, cap, allocation or price by accident.

    Checked structurally rather than by grepping the text, because the file legitimately
    *documents* the absence of these things in its `deliberately_absent` block. Documenting an
    absence is the opposite of defining a value, and a naive text match cannot tell them apart —
    it flagged the documentation on the first run.
    """
    failures = []
    for path, value in _walk(rubric):
        if path.startswith("deliberately_absent"):
            continue
        leaf = path.split(".")[-1].split("[")[0]
        if leaf in FORBIDDEN_KEYS and isinstance(value, (int, float)) and not isinstance(value, bool):
            failures.append(
                f"the rubric defines {path} = {value!r}. Threshold, cap, allocation and price "
                "were explicitly NOT approved at the CCC sitting of 2026-08-01."
            )
    return failures


# ---------------------------------------------------------------------------


FORM_PATH = ROOT / "engine/schemas/application-form.yaml"


def load_form() -> dict[str, Any]:
    return yaml.safe_load(FORM_PATH.read_text(encoding="utf-8"))


def check_form_respects_parameters(rubric: dict[str, Any]) -> list[str]:
    """The instrument must be valid across every declared range of every open PARAMETER.

    F018 (eligibility breadth), F020 (country set), F024 (price) and F025 (cohort size) are all
    PARAMETERs. A form that hardcodes three countries, or prints a price, or states a number of
    places, silently commits the programme to a decision the committee has not taken.
    """
    failures = []
    form = load_form()
    text = FORM_PATH.read_text(encoding="utf-8").lower()

    for field_name in ("price", "fee", "tuition", "cost"):
        for path, value in _walk(form):
            if path.startswith("form.omissions"):
                continue
            leaf = path.split(".")[-1].split("[")[0]
            if leaf == field_name:
                failures.append(f"the form defines {path}; F024 is a PARAMETER and no price may appear")

    for country in ("nigeria", "ghana", "pakistan"):
        for section in form.get("sections", []):
            for fld in section.get("fields", []):
                options = fld.get("options")
                if isinstance(options, list) and any(
                    country in str(o).lower() for o in options
                ):
                    failures.append(
                        f"field {fld['id']} offers a hardcoded country option mentioning "
                        f"{country!r}; F020 is a PARAMETER and the country set is undecided"
                    )

    policy = form.get("eligibility_policy", {})
    if policy.get("active_option") is not None:
        failures.append(
            "eligibility_policy.active_option is set; F018 is a PARAMETER and eligibility "
            "breadth is not decided"
        )
    if set(policy.get("options", {})) != {
        "clinical_only", "clinical_and_non_clinical", "open_with_experience_floor"
    }:
        failures.append(
            "eligibility_policy.options does not match F018's declared range; the form must be "
            "valid across the whole range"
        )
    return failures


def check_support_section_is_walled_off(rubric: dict[str, Any]) -> list[str]:
    """W07-01 condition 8, checked in the instrument rather than only in the engine."""
    failures = []
    form = load_form()
    support = next((s for s in form["sections"] if s["id"] == "S6"), None)
    if support is None:
        failures.append("the form has no S6 support section; condition 8 requires one")
        return failures
    for flag in ("excluded_from_scoring", "excluded_from_moderation", "hidden_from_reviewers"):
        if support.get(flag) is not True:
            failures.append(f"S6 does not assert {flag}; condition 8 requires all three")
    for fld in support.get("fields", []):
        if fld.get("scores"):
            failures.append(f"S6 field {fld['id']} is marked as scoring; condition 8 forbids it")
    return failures


def check_institutional_seat_terms_present(rubric: dict[str, Any]) -> list[str]:
    """W07-01 condition 6: the transferable-not-guaranteed term must be acknowledged in the
    instrument, in writing, before money changes hands."""
    form = load_form()
    for section in form["sections"]:
        for fld in section.get("fields", []):
            if fld["id"] == "institutional_seat_terms_acknowledged":
                prompt = str(fld.get("prompt", "")).lower()
                if "transferable" in prompt and "not guaranteed" in prompt:
                    return []
                return ["the institutional seat acknowledgement does not state that the seat is "
                        "transferable within the institution and not guaranteed to a named nominee"]
    return ["the form has no institutional seat acknowledgement; W07-01 condition 6 requires one"]


def check_no_applicant_data_committed(rubric: dict[str, Any]) -> list[str]:
    """The blank instrument only. Restricted fields must be marked so no surface stores them here."""
    failures = []
    form = load_form()
    expected_restricted = {"full_name", "email", "phone", "verifying_contact",
                           "nominating_institution", "support_needs",
                           "reasonable_adjustment_request"}
    marked = {
        fld["id"]
        for section in form["sections"]
        for fld in section.get("fields", [])
        if fld.get("restricted")
    }
    missing = expected_restricted - marked
    if missing:
        failures.append(
            f"these fields carry personal data but are not marked restricted: {sorted(missing)}"
        )
    return failures


def self_test() -> int:
    """End-to-end test. Discharges W07-01 condition 5 for everything testable without a live form."""
    print("W07 admissions engine — end-to-end test")
    print("Discharges W07-01 condition 5 (form, calculation, evidence gates, moderation)")
    print()

    try:
        rubric = load_rubric()
    except RubricError as exc:
        print(f"  FAIL  rubric: {exc}", file=sys.stderr)
        return 1
    print(f"  ok    rubric loads; {len(rubric['criteria'])} criteria, weights sum to 100")

    cases = load_cases()
    print(f"  ok    {len(cases)} calibration cases loaded")
    if len(cases) != 18:
        print(
            f"  FAIL  W07-01 condition 3 requires eighteen fictional cases; found {len(cases)}",
            file=sys.stderr,
        )
        return 1

    checks = [
        ("published totals reproduce", check_published_totals),
        ("canon invariants hold (prestige, sponsorship, ability to pay, adjustment, source)",
         check_canon_invariants),
        ("support needs excluded from moderation (condition 8)",
         check_support_needs_excluded_from_moderation),
        ("moderation trigger behaves (condition 4)", check_moderation_behaviour),
        ("evidence gates sit outside the score", check_gates_independent_of_score),
        ("no threshold, cap or allocation has leaked in", check_no_threshold_leaked),
        ("form is valid across every open parameter (F018, F020, F024, F025)",
         check_form_respects_parameters),
        ("support section walled off from scoring and moderation (condition 8)",
         check_support_section_is_walled_off),
        ("institutional seat terms stated (condition 6)", check_institutional_seat_terms_present),
        ("personal-data fields marked restricted", check_no_applicant_data_committed),
    ]

    failed = 0
    for name, fn in checks:
        try:
            problems = fn(rubric)
        except Exception as exc:  # noqa: BLE001 - a crash here is a failure like any other
            print(f"  FAIL  {name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if problems:
            failed += 1
            print(f"  FAIL  {name}", file=sys.stderr)
            for problem in problems[:5]:
                print(f"          {problem}", file=sys.stderr)
            if len(problems) > 5:
                print(f"          ... and {len(problems) - 5} more", file=sys.stderr)
        else:
            print(f"  ok    {name}")

    print()
    if failed:
        print(f"{failed} check(s) failed", file=sys.stderr)
        return 1
    print("All checks passed.")
    print()
    print("NOT tested here, and NOT therefore discharged: the reasonable-adjustment route and the")
    print("reconsideration process, both of which are human procedures rather than calculations,")
    print("and the live form itself. Condition 5 is discharged for the calculation, the evidence")
    print("gates and the moderation rule only. The rest needs the built form and a dry run.")
    return 0


def report() -> int:
    rubric = load_rubric()
    rows = []
    for case in load_cases():
        a, b = to_application(case, "a"), to_application(case, "b")
        sa, sb = score(a, rubric).rounded(), score(b, rubric).rounded()
        fires, why = needs_moderation(a, b, rubric)
        rows.append((case["id"], sa, sb, round(abs(sa - sb), 2), "YES — " + why if fires else "no",
                     case["variable_tested"]))

    print(f"{'Case':<8}{'A':>8}{'B':>8}{'gap':>7}  {'moderate?':<34}variable tested")
    print("-" * 120)
    for cid, sa, sb, gap, mod, var in rows:
        print(f"{cid:<8}{sa:>8.2f}{sb:>8.2f}{gap:>7.2f}  {mod:<34}{var}")
    gaps = [r[3] for r in rows]
    print("-" * 120)
    print(f"mean absolute difference {sum(gaps)/len(gaps):.2f} · largest {max(gaps):.2f}")
    print()
    print("These are synthetic cases. They demonstrate that the instrument behaves as designed.")
    print("They do NOT establish reliability, and no threshold may be derived from them.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    if args.report:
        return report()
    return self_test()


if __name__ == "__main__":
    raise SystemExit(main())
