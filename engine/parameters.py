#!/usr/bin/env python3
"""Refuse to ship a build that has quietly resolved an open decision.

WHY THIS EXISTS
---------------
The instruction was that nothing is hardwired: the design works across whatever
range a decision might land in, and the committee resolves it afterwards. Several
files say so. Until now nothing checked it.

A promise no test enforces decays quietly, and the decay is never a decision
anyone remembers making. Someone adds a price to a form because the page needed a
number. Someone turns a free-entry country field into a dropdown of three because
a dropdown is tidier. Someone sets an eligibility option because null looked
unfinished. No one intends to close the parameter; it closes anyway, and the
committee is then presented with a fait accompli wearing the language of an open
question.

So this module makes the promise executable:

  1. HARDCODING. For every parameter still open, a resolved value must not appear
     in any artefact the programme runs on. Declared in
     engine/schemas/parameter-guards.yaml as textual patterns and — preferred
     where the shape allows — structural assertions, which are stronger because
     deleting the declaration of absence is itself a failure.

  2. BUILD POSTURE. Every open parameter must say what IS built while it stays
     open. A parameter that only declares what it blocks teaches the engine, and
     the reader, that openness is a stop. Openness is an instruction to build
     configurable.

  3. RECOMMENDATION OR A STATED REASON. Every open parameter carries a
     recommendation, or an explicit entry saying why it cannot. An empty research
     queue and an unnoticed gap look identical otherwise.

WHERE THE GUARDS DO NOT APPLY
-----------------------------
canon declares the range — that is its job. Recommendations name a value on
purpose. Research must be able to discuss figures. A guard firing on any of those
would make the range undeclarable, the recommendation unwritable, and the
research impossible. Only build artefacts are scanned.

Usage:
    python3 engine/parameters.py
    python3 engine/parameters.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GUARDS_PATH = ROOT / "engine/schemas/parameter-guards.yaml"

sys.path.insert(0, str(ROOT / "engine"))
import decision_interview as di  # noqa: E402

_URL_RE = re.compile(r"https?://\S+")


def load_guards() -> dict[str, Any]:
    if not GUARDS_PATH.is_file():
        raise SystemExit(f"{GUARDS_PATH.relative_to(ROOT)} does not exist.")
    return yaml.safe_load(GUARDS_PATH.read_text(encoding="utf-8"))


def open_parameters() -> dict[str, Any]:
    return {k: v for k, v in di.load_facts().items() if v.get("status") == "PARAMETER"}


def _dig(doc: Any, dotted: str) -> tuple[bool, Any]:
    """Walk a dotted path. Returns (present, value)."""
    node = doc
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


# ---------------------------------------------------------------------------

def check_hardcoding(guards: dict[str, Any], facts: dict[str, Any]) -> list[str]:
    """No artefact may carry a resolved value for a parameter that is still open."""
    problems: list[str] = []
    artefacts = guards.get("build_artefacts") or []

    for guard in guards.get("guards") or []:
        param = guard["parameter"]
        if param not in facts:
            continue  # resolved and promoted, or superseded: the guard retires with it

        # --- textual ---------------------------------------------------
        for pattern in guard.get("patterns") or []:
            compiled = re.compile(pattern, re.IGNORECASE)
            for rel in artefacts:
                path = ROOT / rel
                if not path.is_file():
                    continue
                for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
                    if line.lstrip().startswith("#"):
                        continue          # a comment explaining the rule is not breaking it
                    # A citation is somebody else's published figure, not ours.
                    if compiled.search(_URL_RE.sub(" ", line)):
                        problems.append(
                            f"{rel}:{number} carries what looks like "
                            f"{guard['resolved_value_is']}, but that decision is still open. "
                            f"The build must work across the whole range until the committee "
                            f"resolves it."
                        )

        # --- structural ------------------------------------------------
        for rule in guard.get("structural") or []:
            path = ROOT / rule["artefact"]
            if not path.is_file():
                problems.append(f"{rule['artefact']} is named by a guard but does not exist")
                continue
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))

            if "must_declare_absent" in rule:
                present, _ = _dig(doc, rule["must_declare_absent"])
                if not present:
                    problems.append(
                        f"{rule['artefact']} no longer declares "
                        f"'{rule['must_declare_absent']}'. While this decision is open the "
                        f"artefact must state the absence positively — deleting the statement "
                        f"is how an absence turns into an oversight."
                    )
            if "must_be_null" in rule:
                present, value = _dig(doc, rule["must_be_null"])
                if not present:
                    problems.append(
                        f"{rule['artefact']} is missing '{rule['must_be_null']}'"
                    )
                elif value is not None:
                    problems.append(
                        f"{rule['artefact']}: '{rule['must_be_null']}' is set to {value!r}. "
                        f"Setting it IS the decision, taken by whoever edited the file rather "
                        f"than by the committee."
                    )

    # Absences belonging to no single parameter. Keyed only to parameters, the
    # guards left the rubric's score threshold entirely unguarded.
    for rule in guards.get("always_declared_absent") or []:
        path = ROOT / rule["artefact"]
        if not path.is_file():
            problems.append(f"{rule['artefact']} is named by a guard but does not exist")
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        present, _ = _dig(doc, rule["path"])
        if not present:
            problems.append(
                f"{rule['artefact']} no longer declares '{rule['path']}'. {rule['why'].strip()}"
            )
    return problems


def check_build_posture(facts: dict[str, Any]) -> list[str]:
    """Every open parameter must say what is BUILT while it stays open."""
    problems = []
    for fact_id, fact in sorted(facts.items()):
        param = fact.get("parameter") or {}
        # design_valid_across_range is a boolean assertion; built_across_range is
        # the account of HOW. The boolean alone was accepted while the accounts
        # were being written; it is not accepted now, because a flag saying "this
        # is fine" is exactly the kind of promise that decays unread.
        if not param.get("built_across_range"):
            problems.append(
                f"{fact_id} declares what it blocks but not what is built while it is open. "
                f"An open parameter is an instruction to build across the range, not a stop."
            )
        elif len(str(param["built_across_range"]).split()) < 20:
            problems.append(
                f"{fact_id}: its account of what is built is too thin to tell a reviewer "
                f"anything. Say what specifically flexes and what does not."
            )
    return problems


def check_recommendation_or_reason(facts: dict[str, Any], guards: dict[str, Any]) -> list[str]:
    """A gap must be explained, not merely empty."""
    registry = di.load_recommendations()
    pending = guards.get("research_pending") or {}
    problems = []
    for fact_id in sorted(facts):
        if fact_id in registry or f"ST-{fact_id}" in registry:
            continue
        reason = pending.get(fact_id)
        if not reason:
            problems.append(
                f"{fact_id} has no recommendation and no stated reason for not having one. "
                f"Add the recommendation, or record in parameter-guards.yaml why research "
                f"cannot produce one — an unexplained gap is indistinguishable from an "
                f"unnoticed one."
            )
        elif len(reason.split()) < 12:
            problems.append(
                f"{fact_id}: the reason for having no recommendation is too thin to act on."
            )
    return problems


# ---------------------------------------------------------------------------

def run() -> int:
    guards = load_guards()
    facts = open_parameters()

    checks = [
        ("no open decision is hardcoded into the build", lambda: check_hardcoding(guards, facts)),
        ("every open parameter declares what is built meanwhile", lambda: check_build_posture(facts)),
        ("every open parameter has a recommendation or a stated reason",
         lambda: check_recommendation_or_reason(facts, guards)),
    ]

    print("Open decisions — the build must not have resolved them")
    print(f"Guarding {len(facts)} open parameter(s): {', '.join(sorted(facts))}\n")

    failed = 0
    for label, fn in checks:
        problems = fn()
        if problems:
            failed += 1
            print(f"  FAIL  {label}")
            for problem in problems:
                print(f"          {problem}")
        else:
            print(f"  ok    {label}")

    print()
    if failed:
        print(f"{failed} check(s) failed.", file=sys.stderr)
        return 1
    print("All checks passed. Every open decision is still genuinely open.")
    return 0


def self_test() -> int:
    """Prove each guard bites, by breaking the build on purpose and restoring it."""
    import copy
    failures: list[str] = []
    guards = load_guards()
    facts = open_parameters()

    if check_hardcoding(guards, facts):
        failures.append("the repository does not currently pass its own guards")

    form = ROOT / "engine/schemas/application-form.yaml"
    rubric = ROOT / "engine/schemas/admissions-rubric.yaml"

    def probe(path: Path, mutate, expect: str, label: str) -> None:
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(mutate(original), encoding="utf-8")
            found = check_hardcoding(load_guards(), open_parameters())
            if not any(expect.lower() in p.lower() for p in found):
                failures.append(f"guard did not bite: {label} (found {found or 'nothing'})")
        finally:
            path.write_text(original, encoding="utf-8")

    # a price written onto the application form
    probe(form, lambda s: s + '\nprice_note: "The fee is USD 500."\n',
          "tuition figure", "a tuition figure added to the application form")

    # the eligibility decision taken by editing a file
    probe(form, lambda s: s.replace("active_option: null", "active_option: clinical_only"),
          "IS the decision", "eligibility resolved by setting active_option")

    # the declaration of absence quietly deleted
    probe(rubric, lambda s: s.replace("  score_threshold: >-", "  score_threshold_REMOVED: >-"),
          "no longer declares", "the rubric's stated absence deleted")

    # a country dropdown hardcoded
    probe(form, lambda s: s + "\nctry:\n  options: [Nigeria, Ghana, Pakistan]\n",
          "fixed list of countries", "a hardcoded country list")

    # a cohort cap stated as places
    probe(form, lambda s: s + '\ncap_note: "There are 40 places."\n',
          "number of places", "a cohort size stated on the form")

    # a comment explaining the rule must NOT trip it
    original_form = form.read_text(encoding="utf-8")
    form.write_text(original_form + '\n# never write "The fee is USD 500." here\n', encoding="utf-8")
    if check_hardcoding(load_guards(), open_parameters()):
        failures.append("a comment explaining the rule was treated as breaking it")
    form.write_text(original_form, encoding="utf-8")

    # build posture and recommendation checks must pass as the repository stands
    for label, problems in [("build posture", check_build_posture(facts)),
                            ("recommendation or reason",
                             check_recommendation_or_reason(facts, guards))]:
        if problems:
            failures.append(f"{label}: {problems[0]}")

    # an unexplained gap must fail
    stripped = copy.deepcopy(guards)
    stripped["research_pending"] = {}
    if not check_recommendation_or_reason(facts, stripped):
        failures.append("a parameter with no recommendation and no reason was accepted")

    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}", file=sys.stderr)
        return 1
    print(f"parameters self-test: all checks passed ({len(facts)} open parameters guarded)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    return self_test() if args.self_test else run()


if __name__ == "__main__":
    raise SystemExit(main())
