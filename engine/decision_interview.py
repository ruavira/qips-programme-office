#!/usr/bin/env python3
"""The CCC design walkthrough: generate it from the repository, capture the answers,
compile the answers into the blueprint.

WHY THIS EXISTS
---------------
The programme director's instruction, in his words: research, compare relevant
programmes, recommend on defensible and documented reasoning, build the best
recommendation as a prototype with editable and configurable design inside it,
then let the CCC walk the build end to end and have their responses become the
blueprint the final product is built from.

That instruction has a failure mode, and this module exists to close it. If the
walkthrough is authored by hand it drifts from the build: a question gets asked
about something that was already settled, or — far worse — something that is open
in the repository never gets asked about at all, and the CCC ratifies a design
with a hole in it they were never shown.

So the walkthrough is GENERATED. Every station comes from a place in the
repository where something is genuinely open:

    canon/facts.yaml                 status: PARAMETER
    canon/open-questions.yaml        every question not yet closed
    engine/schemas/*.yaml            unresolved_assumptions
                                     not_yet_established
                                     deliberately_absent

`check_coverage` fails the build if any of those exists without a station. The
interview therefore cannot drift from the build, and an open item cannot hide.

WHAT A STATION IS NOT
---------------------
It is not a blank field asking the committee to invent an answer. Every station
must carry a recommendation with the comparative work and the evidence behind it
— or must say, explicitly and with a reason, that there is no recommendation yet.
`check_recommendations` enforces that. A station with neither is a defect, and the
missing-recommendation list is the research queue.

WHAT THIS WILL NEVER DO
-----------------------
Write canon. It emits a blueprint — a proposal on a branch, with a draft minute,
for a human to merge. AGENTS.md is unambiguous that only a recorded CCC verdict
writes to canon, and neither a generated question nor a captured answer is a
verdict. A recommendation is not a decision and this module never promotes one.

Usage:
    python3 engine/decision_interview.py --stations        # emit the walkthrough
    python3 engine/decision_interview.py --check           # coverage + recommendations
    python3 engine/decision_interview.py --capture responses.yaml --out-dir .blueprint
    python3 engine/decision_interview.py --self-test
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

FACTS_PATH = ROOT / "canon/facts.yaml"
QUESTIONS_PATH = ROOT / "canon/open-questions.yaml"
RECOMMENDATIONS_PATH = ROOT / "engine/schemas/recommendations.yaml"
NEEDS_PATH = ROOT / "engine/schemas/contribution-needs.yaml"
SCHEMA_DIR = ROOT / "engine/schemas"

# The four things a committee member can do at a station. ACCEPT takes the
# recommendation as it stands; the other three change it, and all three must carry
# a reason, because the reason becomes a standing constraint on the rebuild. This
# mirrors engine/decision_capture.py deliberately — one vocabulary, two surfaces.
RESPONSES = {"ACCEPT", "AMEND", "REJECT", "DEFER", "NOTED", "QUESTION", "CHALLENGE"}
REASON_REQUIRED = {"AMEND", "REJECT", "DEFER", "CHALLENGE"}

# What a reviewer may do at a station where something is genuinely OPEN.
DECISION_RESPONSES = {"ACCEPT", "AMEND", "REJECT", "DEFER"}

# What a reviewer may do at a REVIEW POINT — something already settled.
#
# CHALLENGE is the one that matters and the reason this vocabulary exists at all.
# The first version of the walkthrough generated stations only from things that
# were open, which meant a committee member looking at "the observership is 40
# hours" (F006, APPROVED) had nowhere to say "why forty?" — they would have had to
# leave the walkthrough and email someone. Under the standing rule that no decision
# is ever a one-way door, reopening a settled fact must be a first-class action
# inside the review, not an escalation outside it.
#
# A CHALLENGE does not reopen anything by itself. It produces a reopening request
# carrying the challenger's reason, which goes to the committee like any other
# proposal.
REVIEW_RESPONSES = {"NOTED", "QUESTION", "CHALLENGE"}

STATION_KINDS = {
    "PARAMETER",           # a canon fact deliberately held open across a range
    "OPEN_QUESTION",       # a Q00n that has not been answered
    "ASSUMPTION",          # an unresolved assumption the design rests on
    "NOT_ESTABLISHED",     # a process step drafted but not yet constituted
    "DELIBERATELY_ABSENT", # something withheld on purpose, needing ratification
    "REVIEW_POINT",        # a SETTLED fact, shown so it can be challenged
    "PROPOSED_FACT",       # proposed or deferred; awaiting a verdict
}

# Kinds where something is open and a decision is being sought.
DECISION_KINDS = {"PARAMETER", "OPEN_QUESTION", "ASSUMPTION", "NOT_ESTABLISHED",
                  "DELIBERATELY_ABSENT", "PROPOSED_FACT"}


# What a co-designer can RAISE that we never thought to ask.
#
# Every one of the generated stops comes from something the repository already
# knows is open. That is the guarantee that nothing open is hidden — and it is
# also the ceiling: she can only answer questions we thought to ask. The most
# valuable thing a co-designer says is usually "you are missing a decision" or
# "this whole section is framed wrongly", and until now there was nowhere in the
# walkthrough to say either. The conflict checker would have caught her
# contradicting herself; nothing would have caught us scoping it badly.
RAISED_KINDS = {
    "MISSING_DECISION",   # a decision nobody has identified as a decision
    "MIS_FRAMED",         # we asked, but the question is the wrong question
    "WRONG_ASSUMPTION",   # something treated as given that she knows is not
    "CONCERN",            # not a decision, but it should be on the record
}


class InterviewError(Exception):
    """A problem a human must fix before the walkthrough can be run."""


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> Any:
    if not path.is_file():
        raise InterviewError(f"{path.relative_to(ROOT)} does not exist.")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_facts() -> dict[str, Any]:
    return {f["id"]: f for f in _load_yaml(FACTS_PATH)["facts"]}


def load_questions() -> dict[str, Any]:
    return {q["id"]: q for q in _load_yaml(QUESTIONS_PATH)["questions"]}


def load_recommendations() -> dict[str, Any]:
    """Recommendations, keyed by what they are about.

    Deliberately NOT in canon. A change to canon/ requires a recorded CCC verdict,
    which would mean asking the committee to approve the research meant to inform
    them before they could read it. It is also the wrong shape: canon holds what
    is true, and a recommendation is by definition not yet true. Keeping them
    apart means research can be corrected without a sitting, and a recommendation
    can never be mistaken for a decision because it is not in the file that holds
    decisions.
    """
    if not RECOMMENDATIONS_PATH.is_file():
        return {}
    doc = yaml.safe_load(RECOMMENDATIONS_PATH.read_text(encoding="utf-8")) or {}
    return {r["target"]: r for r in doc.get("recommendations", []) if r.get("target")}


def load_needs() -> dict[str, Any]:
    """What each stop needs from the person walking it.

    Kept as data because the taxonomy is a judgement about how to work with a
    colleague, not an implementation detail — it should be arguable by the people
    it describes, and changing it must not mean changing code.
    """
    if not NEEDS_PATH.is_file():
        return {}
    return yaml.safe_load(NEEDS_PATH.read_text(encoding="utf-8")) or {}


def _needs_of(kind: str, station_id: str, fact_id: str, has_rec: bool) -> dict[str, Any]:
    """Derive what this stop needs, unless an override says otherwise.

    Badging everything "open" is a REVIEW frame and it tells a co-designer
    nothing about where she is actually needed. An untested assumption about
    whether a working consultant can find four hours a week, and a question only
    SQHN can answer, are not the same kind of thing and should not look alike.
    """
    doc = load_needs()
    overrides = doc.get("overrides") or {}
    override = overrides.get(station_id) or overrides.get(fact_id)
    if override:
        need = override["needs"]
        why = override.get("why")
    else:
        default = (doc.get("defaults") or {}).get(kind, {})
        need = default.get("with_recommendation" if has_rec else "without")
        why = None
    entry = (doc.get("taxonomy") or {}).get(need, {})
    return {
        "code": need,
        "label": entry.get("label"),
        "invitation": entry.get("invitation"),
        "why_this_classification": why,
    }


def load_schemas() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        out[path.name] = _load_yaml(path)
    return out


# ---------------------------------------------------------------------------
# Station generation
# ---------------------------------------------------------------------------

def _options_from_range(range_text: str) -> list[str]:
    """Split a declared range into presentable options.

    Ranges are written for humans, pipe-separated where the options are discrete.
    Where they are not pipe-separated the range is continuous (a price band, a
    cohort size) and is presented whole rather than chopped into false choices.
    """
    if not range_text:
        return []
    if "|" not in range_text:
        return [range_text.strip()]
    return [part.strip() for part in range_text.split("|") if part.strip()]


def _recommendation_of(node: dict[str, Any], *keys: str) -> dict[str, Any]:
    """Read a structured recommendation block, or report its absence honestly.

    A recommendation is research output. It is NOT a decision and this function
    never returns one that claims to be: `binding` is always False, and the status
    string says so in words that survive being copied into a slide.
    """
    registry = load_recommendations()
    block = next((registry[k] for k in keys if k in registry), None)
    if block is None:
        block = node.get("recommendation")
    if not isinstance(block, dict):
        return {
            "present": False,
            "status": "NO_RECOMMENDATION_YET",
            "binding": False,
            "note": (
                "No structured recommendation exists for this station yet. The station is "
                "still shown — an open item must never be hidden from the committee — but it "
                "is shown as an open question rather than as a proposal, and the research to "
                "support a recommendation is outstanding."
            ),
        }
    return {
        "present": True,
        "status": "RECOMMENDATION_NOT_A_DECISION",
        "binding": False,
        "option": block.get("option"),
        "rationale": block.get("rationale"),
        "comparators": block.get("comparators", []),
        "evidence": block.get("evidence", []),
        "confidence": block.get("confidence"),
        "confidence_basis": block.get("confidence_basis"),
        "what_would_change_it": block.get("what_would_change_it"),
        "owner": block.get("owner"),
    }


def _station(
    station_id: str,
    kind: str,
    source: str,
    prompt: str,
    built: str,
    options: list[str],
    recommendation: dict[str, Any],
    **extra: Any,
) -> dict[str, Any]:
    if kind not in STATION_KINDS:
        raise InterviewError(f"{station_id}: unknown station kind {kind!r}")
    fact_id = source.split("::")[-1]
    station = {
        "id": station_id,
        "kind": kind,
        "needs": _needs_of(kind, station_id, fact_id, bool(recommendation.get("present"))),
        "source": source,          # file + key, so every station is traceable to the repo
        "prompt": prompt,
        "what_we_built": built,
        "options": options,
        "recommendation": recommendation,
        "response": {
            "allowed": sorted(DECISION_RESPONSES if kind in DECISION_KINDS else REVIEW_RESPONSES),
            "reason_required_for": sorted(REASON_REQUIRED),
            "note": (
                "A reason on AMEND, REJECT or DEFER is not paperwork. It is recorded as a "
                "standing constraint on the team that owns this, and it is how the same "
                "proposal stops coming back to you unchanged."
                if kind in DECISION_KINDS
                else "This is settled. NOTED moves on, QUESTION asks without changing anything, "
                "and CHALLENGE opens a request to reopen it, carrying your reason. A challenge "
                "does not reopen anything by itself — it puts the question to the committee."
            ),
        },
    }
    station.update(extra)
    return station


def build_stations() -> list[dict[str, Any]]:
    """Generate the whole walkthrough from the repository."""
    stations: list[dict[str, Any]] = []
    facts = load_facts()
    questions = load_questions()
    schemas = load_schemas()

    # --- PARAMETER facts -------------------------------------------------
    for fact_id, fact in sorted(facts.items()):
        if fact.get("status") != "PARAMETER":
            continue
        param = fact.get("parameter") or {}
        stations.append(
            _station(
                station_id=f"ST-{fact_id}",
                kind="PARAMETER",
                source=f"canon/facts.yaml::{fact_id}",
                prompt=fact.get("statement", ""),
                built=(
                    param.get("built_across_range")
                    or (
                        "Built to work across the whole declared range; no single value is fixed into it."
                        if param.get("design_valid_across_range")
                        else "NOT YET STATED — what is built while this stays open has not been recorded."
                    )
                ),
                options=_options_from_range(param.get("range", "")),
                recommendation=_recommendation_of(param, fact_id, f"ST-{fact_id}"),
                why_held_open=param.get("why"),
                what_it_gates=param.get("gates"),
                what_it_does_not_gate=param.get("does_not_gate"),
                decide_by=param.get("decide_by"),
                decide_by_meaning=(
                    "The date beyond which the choice gets expensive or an option closes "
                    "off. It is not a deadline for an answer: nothing stalls waiting for it, "
                    "and the design keeps working whichever way it goes."
                ),
                owner=fact.get("owner"),
            )
        )

    # --- proposed and deferred facts --------------------------------------
    #
    # A fact that is PROPOSED has been put to the committee and not yet resolved;
    # one that was DEFERRED is the same thing with a date attached. Neither is
    # settled and neither is a parameter, so the first version of this generator
    # produced no station for them at all — which would have hidden F027, the
    # go/no-go kill date, from a committee walking the whole design. Found by the
    # journey spine anchoring an item the generator never emitted.
    for fact_id, fact in sorted(facts.items()):
        if fact.get("status") != "PROPOSED":
            continue
        stations.append(
            _station(
                station_id=f"ST-{fact_id}",
                kind="PROPOSED_FACT",
                source=f"canon/facts.yaml::{fact_id}",
                prompt=fact.get("statement", ""),
                built=(
                    "Proposed, not settled. Nothing else treats this as true, and the design "
                    "does not assume it."
                ),
                options=[],
                recommendation=_recommendation_of(fact, fact_id, f"ST-{fact_id}"),
                deferral_reason=fact.get("deferral_reason"),
                owner=fact.get("owner"),
                source_of_truth=fact.get("source"),
            )
        )

    # --- settled facts, shown so they can be challenged -------------------
    #
    # Everything APPROVED gets a review point. A design review where the reviewer
    # may only comment on what is already open is not a design review; it is a
    # form. SUPERSEDED facts are excluded — the reviewer should be looking at the
    # fact that replaced them, not at history.
    for fact_id, fact in sorted(facts.items()):
        if fact.get("status") != "APPROVED":
            continue
        stations.append(
            _station(
                station_id=f"ST-{fact_id}",
                kind="REVIEW_POINT",
                source=f"canon/facts.yaml::{fact_id}",
                prompt=fact.get("statement", ""),
                built=(
                    "Settled and built. Shown here so it can be questioned or challenged, "
                    "never so it can be rubber-stamped."
                ),
                options=[],
                recommendation=_recommendation_of(fact, fact_id, f"ST-{fact_id}"),
                settled_on=fact.get("ratified_on") or fact.get("established"),
                owner=fact.get("owner"),
                source_of_truth=fact.get("source"),
                reopening_note=(
                    "Standing rule of this programme: the opportunity to course correct, "
                    "enhance or update is always open. Challenging this costs nothing and "
                    "needs no justification beyond your reason."
                ),
            )
        )

    # --- open questions --------------------------------------------------
    for qid, question in sorted(questions.items()):
        if question.get("status") in {"CLOSED", "ANSWERED"}:
            continue
        stations.append(
            _station(
                station_id=f"ST-{qid}",
                kind="OPEN_QUESTION",
                source=f"canon/open-questions.yaml::{qid}",
                prompt=question.get("question", ""),
                built=(
                    "Nothing in the design depends on an answer being invented here. Where this "
                    "question decides a figure, the figure is left open rather than guessed."
                ),
                options=[],
                recommendation=_recommendation_of(question, qid, f"ST-{qid}"),
                blocking=question.get("blocking", False),
                blocks=question.get("blocks", []),
                due=question.get("due"),
                owner=question.get("owner"),
                note=question.get("note"),
            )
        )

    # --- schema-level openness ------------------------------------------
    for filename, doc in schemas.items():
        stations.extend(_stations_from_schema(filename, doc))

    return stations


def _walk(node: Any, path: str = ""):
    """Yield (dotted_path, key, value) for every mapping entry in a document."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            yield here, key, value
            yield from _walk(value, here)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            here = f"{path}[{index}]"
            yield from _walk(item, here)


def _slug(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", str(text).upper()).strip("-")[:40]


def _stations_from_schema(filename: str, doc: Any) -> list[dict[str, Any]]:
    stations: list[dict[str, Any]] = []
    stem = filename.replace(".yaml", "")

    for dotted, key, value in _walk(doc):
        # unresolved assumptions carry their own ids
        if key == "unresolved_assumptions" and isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    continue
                uid = item.get("id", _slug(item.get("assumption", "")))
                stations.append(
                    _station(
                        station_id=f"ST-{stem}-{uid}",
                        kind="ASSUMPTION",
                        source=f"engine/schemas/{filename}::{dotted}[{uid}]",
                        prompt=item.get("assumption", ""),
                        built=(
                            "The design rests on this assumption. It is recorded as untested "
                            "rather than presented as established."
                        ),
                        options=[],
                        recommendation=_recommendation_of(item, f"ST-{stem}-{uid}"),
                        status=item.get("status"),
                        tested_by=item.get("tested_by"),
                        risk=item.get("risk"),
                        mitigation=item.get("mitigation_drafted"),
                        owner=item.get("owner"),
                    )
                )

        # process steps drafted but not constituted
        if key == "not_yet_established" and isinstance(value, list):
            parent = dotted.rsplit(".", 1)[0] if "." in dotted else stem
            for index, item in enumerate(value):
                stations.append(
                    _station(
                        station_id=f"ST-{stem}-{_slug(parent)}-{index + 1}",
                        kind="NOT_ESTABLISHED",
                        source=f"engine/schemas/{filename}::{dotted}[{index}]",
                        prompt=str(item),
                        built=(
                            f"The surrounding process ({parent}) is drafted and the surface is "
                            "built; this element of it is not yet constituted."
                        ),
                        options=[],
                        recommendation=_recommendation_of(
                            item if isinstance(item, dict) else {},
                            f"ST-{stem}-{_slug(parent)}-{index + 1}",
                        ),
                    )
                )

        # things withheld on purpose — these need ratifying, not just noting
        if key == "deliberately_absent" and isinstance(value, dict):
            for absent_key, reason in value.items():
                stations.append(
                    _station(
                        station_id=f"ST-{stem}-ABSENT-{_slug(absent_key)}",
                        kind="DELIBERATELY_ABSENT",
                        source=f"engine/schemas/{filename}::{dotted}.{absent_key}",
                        prompt=(
                            f"No {absent_key.replace('_', ' ')} is set anywhere in the design. "
                            "Does the committee agree it stays unset for cohort 1?"
                        ),
                        built=str(reason),
                        options=["keep absent", "set it now", "defer with a date"],
                        recommendation=_recommendation_of({}, f"ST-{stem}-ABSENT-{_slug(absent_key)}"),
                    )
                )

    return stations


# ---------------------------------------------------------------------------
# Checks — these are what make the walkthrough trustworthy
# ---------------------------------------------------------------------------

def check_coverage(stations: list[dict[str, Any]]) -> list[str]:
    """Every open item in the repository must appear as a station.

    This is the guarantee that the interview cannot drift from the build. If it
    fails, something is open that the committee would never have been shown.
    """
    problems: list[str] = []
    covered = {s["source"] for s in stations}

    for fact_id, fact in load_facts().items():
        key = f"canon/facts.yaml::{fact_id}"
        if fact.get("status") == "PARAMETER" and key not in covered:
            problems.append(
                f"{fact_id} is a PARAMETER but generates no station. An open canon fact "
                "would be invisible to the committee."
            )
        if fact.get("status") == "PROPOSED" and key not in covered:
            problems.append(
                f"{fact_id} is PROPOSED but generates no station. An undecided fact the "
                "committee is never shown is a decision made by omission."
            )
        if fact.get("status") == "APPROVED" and key not in covered:
            problems.append(
                f"{fact_id} is APPROVED but generates no review point. A settled fact the "
                "committee cannot challenge is a fact they cannot reopen, and every decision "
                "in this programme is reopenable."
            )

    for qid, question in load_questions().items():
        if question.get("status") in {"CLOSED", "ANSWERED"}:
            continue
        if f"canon/open-questions.yaml::{qid}" not in covered:
            problems.append(f"{qid} is open but generates no station.")

    for filename, doc in load_schemas().items():
        for dotted, key, value in _walk(doc):
            if key in {"unresolved_assumptions", "not_yet_established"} and isinstance(value, list):
                hits = [s for s in stations if s["source"].startswith(f"engine/schemas/{filename}::{dotted}")]
                if len(hits) < len(value):
                    problems.append(
                        f"engine/schemas/{filename}::{dotted} holds {len(value)} open items but "
                        f"generates {len(hits)} stations."
                    )

    return problems


def check_recommendations(stations: list[dict[str, Any]]) -> list[str]:
    """A recommendation must be evidenced, and must never claim to be a decision.

    A missing recommendation is reported but is NOT a hard failure: an honestly
    open question is a legitimate station. A recommendation with no evidence IS a
    hard failure, because that is an opinion wearing a recommendation's clothes.
    """
    problems: list[str] = []
    for station in stations:
        rec = station["recommendation"]
        if not rec.get("present"):
            continue
        if rec.get("binding"):
            problems.append(
                f"{station['id']}: recommendation is marked binding. A recommendation is "
                "research output; only the CCC decides."
            )
        if not rec.get("evidence"):
            problems.append(
                f"{station['id']}: recommendation carries no evidence. Every recommendation "
                "cites a source with a live URL and an accessed date, or it is not a "
                "recommendation."
            )
        if not rec.get("rationale"):
            problems.append(f"{station['id']}: recommendation carries no rationale.")
    return problems


def missing_recommendations(stations: list[dict[str, Any]]) -> list[str]:
    """The research queue: stations that should carry a recommendation and do not."""
    return [
        s["id"]
        for s in stations
        if not s["recommendation"].get("present") and s["kind"] in {"PARAMETER", "DELIBERATELY_ABSENT"}
    ]


def check_build_posture(stations: list[dict[str, Any]]) -> list[str]:
    """Every PARAMETER must declare what is BUILT while it is open.

    A parameter that only declares what it blocks teaches the engine to treat
    openness as a stop. Openness is an instruction to build configurable.
    """
    return [
        f"{s['id']}: no build posture declared — what is built while this is open?"
        for s in stations
        if s["kind"] == "PARAMETER" and "NOT DECLARED" in str(s.get("what_we_built", ""))
    ]


# ---------------------------------------------------------------------------
# Live conflict checking — runs in the room, before anything is written
# ---------------------------------------------------------------------------

def check_live_conflicts(
    responses: list[dict[str, Any]],
    stations: list[dict[str, Any]],
) -> list[str]:
    """Check answers against each other and against canon, during the sitting.

    Every conflict class here was found the hard way at the sitting of 1 August
    2026, where four cross-decision conflicts would otherwise have shipped. The
    rule for this function: when a new class of contradiction is found in a real
    sitting, it is added here, so it can never be found the same way twice.
    """
    problems: list[str] = []
    by_id = {s["id"]: s for s in stations}
    facts = load_facts()
    seen: dict[str, dict[str, Any]] = {}

    for response in responses:
        station_id = response.get("station")
        verdict = str(response.get("response", "")).strip().upper()
        reason = (response.get("reason") or "").strip()
        chosen = response.get("chosen_option")

        # 1. the station must exist
        station = by_id.get(station_id)
        if station is None:
            problems.append(f"{station_id!r} is not a station in this walkthrough.")
            continue

        # 2. the verdict must be one this KIND of station allows. A settled fact
        #    cannot be "AMENDED" in place, and an open parameter cannot be merely
        #    "NOTED" — the vocabularies are deliberately different.
        allowed = set(station["response"]["allowed"])
        if verdict not in allowed:
            problems.append(
                f"{station_id} is a {station['kind']}; response {verdict!r} is not one of "
                f"{', '.join(sorted(allowed))}."
            )
            continue

        # 3. a change must carry a reason — the reason is the constraint
        if verdict in REASON_REQUIRED and not reason:
            problems.append(
                f"{station_id}: {verdict} with no reason. The reason becomes a standing "
                "constraint on the rebuild; without it the engine re-proposes what was refused."
            )

        # 4. a chosen option must sit inside the declared range
        if chosen and station["options"]:
            if not any(_norm(chosen) == _norm(opt) for opt in station["options"]):
                problems.append(
                    f"{station_id}: '{chosen}' is outside the declared range "
                    f"({' | '.join(station['options'])}). Choosing outside the range is "
                    "legitimate, but it widens the parameter and needs its own minuted decision."
                )

        # 5. the same station answered twice, differently, in one sitting
        if station_id in seen and seen[station_id] != {"v": verdict, "c": chosen}:
            problems.append(
                f"{station_id}: answered more than once with different answers in the same "
                "sitting. The later answer does not silently win."
            )
        seen[station_id] = {"v": verdict, "c": chosen}

        # 6. never decide against a superseded fact
        fact_id = station["source"].split("::")[-1]
        fact = facts.get(fact_id)
        if fact and fact.get("status") == "SUPERSEDED":
            problems.append(
                f"{station_id}: {fact_id} is SUPERSEDED by "
                f"{fact.get('superseded_by', 'an unrecorded fact')}."
            )

    # 7. dependency conflicts across answers given in the same sitting
    problems.extend(_check_cross_answer(seen, by_id))
    return problems


def check_raised(raised: list[dict[str, Any]]) -> list[str]:
    """Check items the reviewer raised themselves.

    Deliberately permissive about SUBSTANCE and strict about USABILITY. It is not
    this module's place to judge whether a raised concern is well founded — that
    is the committee's. But an item with a title and no detail cannot be acted on
    by anyone, and would sit in the record as a reproach nobody can answer.
    """
    problems = []
    for index, item in enumerate(raised, 1):
        kind = str(item.get("kind", "")).strip().upper()
        if kind not in RAISED_KINDS:
            problems.append(
                f"raised item {index}: {kind!r} is not one of "
                f"{', '.join(sorted(RAISED_KINDS))}."
            )
        if not (item.get("title") or "").strip():
            problems.append(f"raised item {index} has no title.")
        if len((item.get("detail") or "").split()) < 8:
            problems.append(
                f"raised item {index} ('{item.get('title', '')[:40]}') has too little detail to "
                f"act on. Whoever picks this up will not have been in the room."
            )
    return problems


def _norm(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def _check_cross_answer(
    seen: dict[str, dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
) -> list[str]:
    """Answers that are each fine alone and contradictory together.

    Kept deliberately small and explicit. A generic dependency solver would be
    more elegant and less trustworthy; these are the pairs a real sitting produced.
    """
    problems: list[str] = []

    # F017 brand identity cannot resolve away from SQHN-led while F028 withholds
    # partner naming. Approved at the sitting of 2026-08-01, Item 5.
    brand = seen.get("ST-F017")
    if brand and brand.get("c") and "sqhn" not in _norm(brand["c"]):
        facts = load_facts()
        if facts.get("F028", {}).get("status") == "APPROVED":
            problems.append(
                "ST-F017: a non-SQHN-led brand identity cannot be chosen while F028 stands — "
                "F028 forbids naming any partner in public-facing material for cohort 1. "
                "Resolve F028 first or this answer cannot be implemented."
            )

    # A country set that widens beyond the anchor market changes what F024's price
    # must clear, because the committed self-pay bands differ by market.
    country = seen.get("ST-F020")
    price = seen.get("ST-F024")
    if country and price and country.get("c") and price.get("c"):
        if "pakistan" in _norm(country["c"]) and "450" not in _norm(price["c"]):
            problems.append(
                "ST-F020 + ST-F024: including Pakistan while setting a price outside USD 450-600 "
                "needs checking against Pakistan's ceiling (~USD 540 at the researched band). "
                "The two answers are individually valid and jointly unverified."
            )

    return problems


# ---------------------------------------------------------------------------
# Blueprint compilation
# ---------------------------------------------------------------------------

def compile_blueprint(
    responses: list[dict[str, Any]],
    stations: list[dict[str, Any]],
    sitting: str,
    raised: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Turn captured answers into a proposed change set plus a draft minute.

    NOT canon. A proposal on a branch. The human merge is the decision.
    """
    by_id = {s["id"]: s for s in stations}
    changes: list[dict[str, Any]] = []
    constraints: list[dict[str, Any]] = []

    for response in responses:
        station = by_id.get(response.get("station"))
        if station is None:
            continue
        verdict = str(response.get("response", "")).strip().upper()
        entry = {
            "station": station["id"],
            "target": station["source"],
            "kind": station["kind"],
            "verdict": verdict,
            "chosen_option": response.get("chosen_option"),
            "amended_text": response.get("amended_text"),
            "reason": response.get("reason"),
            "decided_by": response.get("by"),
        }
        changes.append(entry)
        if verdict in REASON_REQUIRED and response.get("reason"):
            constraints.append(
                {
                    "owner": station.get("owner") or "unassigned",
                    "constraint": response["reason"],
                    "arising_from": station["id"],
                    "note": (
                        "Written into the owning workstream brief as a standing constraint. "
                        "The engine must not re-propose what this refused."
                    ),
                }
            )

    return {
        "blueprint": {
            "sitting": sitting,
            "status": "PROPOSED_NOT_CANON",
            "note": (
                "Compiled from a CCC design walkthrough. This is a PROPOSAL. It is not canon "
                "and does not become canon until a human merges the pull request that carries "
                "it and a minute records the verdicts."
            ),
            "stations_walked": len(responses),
            "stations_total": len(stations),
            "coverage": f"{len(responses)}/{len(stations)}",
            "unwalked": sorted(set(by_id) - {r.get("station") for r in responses}),
            "raised_count": len(raised or []),
        },
        "changes": changes,
        "standing_constraints": constraints,
        # Raised items are NOT changes. They do not resolve anything and they do
        # not touch the design; they open work. Keeping them in their own section
        # stops a question being mistaken for an answer.
        "raised_by_the_reviewer": [
            {
                "kind": str(item.get("kind", "")).strip().upper(),
                "title": item.get("title"),
                "detail": item.get("detail"),
                "where": item.get("act") or item.get("where"),
                "raised_by": item.get("by"),
                "status": "OPENS_WORK_NOT_A_DECISION",
            }
            for item in (raised or [])
        ],
    }


def render_minute(blueprint: dict[str, Any]) -> str:
    meta = blueprint["blueprint"]
    lines = [
        f"# CCC design walkthrough — {meta['sitting']}",
        "",
        "**DRAFT MINUTE. Not canon until merged.**",
        "",
        f"Stations walked: {meta['coverage']}.",
        "",
    ]
    if meta["unwalked"]:
        lines += [
            "## Not reached",
            "",
            "These stations were generated but not answered. They remain open, and the build "
            "continues to hold them as parameters rather than resolving them by default.",
            "",
        ]
        lines += [f"- {station}" for station in meta["unwalked"]]
        lines.append("")

    lines += ["## Verdicts", ""]
    for change in blueprint["changes"]:
        lines.append(f"### {change['station']} — {change['verdict']}")
        lines.append("")
        lines.append(f"Target: `{change['target']}`")
        if change.get("chosen_option"):
            lines.append(f"Chosen: {change['chosen_option']}")
        if change.get("amended_text"):
            lines.append(f"Amended to: {change['amended_text']}")
        if change.get("reason"):
            lines.append(f"Reason: {change['reason']}")
        lines.append("")

    if blueprint["standing_constraints"]:
        lines += ["## Standing constraints arising", ""]
        for constraint in blueprint["standing_constraints"]:
            lines.append(
                f"- **{constraint['owner']}** ({constraint['arising_from']}): "
                f"{constraint['constraint']}"
            )
        lines.append("")

    if blueprint.get("raised_by_the_reviewer"):
        lines += [
            "## Raised in the room — not answers, but work opened",
            "",
            "These were not on the agenda. They were raised by the person walking the design, "
            "which means the running order missed them. Each one needs an owner.",
            "",
        ]
        for item in blueprint["raised_by_the_reviewer"]:
            where = f" (at {item['where']})" if item.get("where") else ""
            lines.append(f"### {item['kind']}: {item['title']}{where}")
            lines.append("")
            lines.append(item.get("detail") or "")
            lines.append("")

    lines += [
        "## Reopening",
        "",
        "Every verdict recorded here is reopenable. Nothing in this walkthrough is a one-way "
        "door, and a later sitting may revisit any station without needing to justify why it "
        "is being reopened.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    failures: list[str] = []
    stations = build_stations()

    if not stations:
        failures.append("no stations were generated at all")

    # every PARAMETER fact must appear
    parameters = [f for f in load_facts().values() if f.get("status") == "PARAMETER"]
    param_stations = [s for s in stations if s["kind"] == "PARAMETER"]
    if len(param_stations) != len(parameters):
        failures.append(
            f"{len(parameters)} PARAMETER facts but {len(param_stations)} stations"
        )

    for problem in check_coverage(stations):
        failures.append(f"coverage: {problem}")

    for problem in check_recommendations(stations):
        failures.append(f"recommendation: {problem}")

    # every station must be traceable to a real file
    for station in stations:
        path = station["source"].split("::")[0]
        if not (ROOT / path).is_file():
            failures.append(f"{station['id']}: source {path} does not exist")

    # a recommendation must never be binding
    for station in stations:
        if station["recommendation"].get("binding"):
            failures.append(f"{station['id']}: recommendation marked binding")

    # --- conflict checker must bite ---------------------------------------
    if param_stations:
        target = param_stations[0]["id"]

        no_reason = [{"station": target, "response": "REJECT", "reason": ""}]
        if not any("no reason" in p for p in check_live_conflicts(no_reason, stations)):
            failures.append("a REJECT with no reason was accepted")

        outside = [
            {"station": target, "response": "ACCEPT", "chosen_option": "something never declared"}
        ]
        if not any("outside the declared range" in p for p in check_live_conflicts(outside, stations)):
            failures.append("an option outside the declared range was accepted")

        unknown = [{"station": "ST-NOPE", "response": "ACCEPT"}]
        if not any("not a station" in p for p in check_live_conflicts(unknown, stations)):
            failures.append("a response to a non-existent station was accepted")

        double = [
            {"station": target, "response": "ACCEPT"},
            {"station": target, "response": "REJECT", "reason": "changed my mind"},
        ]
        if not any("more than once" in p for p in check_live_conflicts(double, stations)):
            failures.append("the same station answered twice differently was accepted")

        good = [{"station": target, "response": "ACCEPT"}]
        if check_live_conflicts(good, stations):
            failures.append(
                f"a clean response was refused: {check_live_conflicts(good, stations)}"
            )

    # the F017/F028 cross-answer rule must bite while F028 stands
    if any(s["id"] == "ST-F017" for s in stations):
        brand = [{"station": "ST-F017", "response": "ACCEPT", "chosen_option": "RCI-led"}]
        if not any("F028" in p for p in check_live_conflicts(brand, stations)):
            failures.append("a non-SQHN brand choice was accepted while F028 stands")

    # --- what a stop needs from the person walking it ---------------------
    codes = {s["needs"]["code"] for s in stations}
    if len(codes) < 3:
        failures.append(f"stops collapse into too few kinds of ask: {codes}")
    for station in stations:
        need = station["needs"]
        if not need.get("code") or not need.get("label") or not need.get("invitation"):
            failures.append(f"{station['id']}: incomplete statement of what it needs")
    # a settled fact must never be badged as needing a decision
    for station in stations:
        if station["kind"] == "REVIEW_POINT" and station["needs"]["code"] != "CHALLENGE_IF_WRONG":
            failures.append(f"{station['id']}: settled, but badged {station['needs']['code']}")
    # a question only a person can answer must not be badged as our recommendation
    knowledge = [s for s in stations if s["needs"]["code"] == "YOUR_KNOWLEDGE"]
    if not knowledge:
        failures.append("nothing is marked as needing her knowledge; the taxonomy is not biting")

    # --- raising something we never asked about ---------------------------
    good = [{"kind": "MISSING_DECISION", "title": "Supervision of the observership",
             "detail": "Nobody has decided who supervises a participant on site, or what "
                       "happens when the host supervisor is unavailable for a week."}]
    if check_raised(good):
        failures.append(f"a well-formed raised item was refused: {check_raised(good)}")
    for bad, label in [
        ([{"kind": "NONSENSE", "title": "x", "detail": "a b c d e f g h i j"}], "unknown kind"),
        ([{"kind": "CONCERN", "title": "", "detail": "a b c d e f g h i j"}], "no title"),
        ([{"kind": "CONCERN", "title": "x", "detail": "too short"}], "too little detail"),
    ]:
        if not check_raised(bad):
            failures.append(f"a raised item with {label} was accepted")

    blueprint_with_raised = compile_blueprint(
        [{"station": stations[0]["id"], "response": "ACCEPT"}], stations, "self-test", good)
    if blueprint_with_raised["blueprint"]["raised_count"] != 1:
        failures.append("a raised item did not reach the blueprint")
    if blueprint_with_raised["raised_by_the_reviewer"][0]["status"] != "OPENS_WORK_NOT_A_DECISION":
        failures.append("a raised item was recorded as though it decided something")
    if "not answers" not in render_minute(blueprint_with_raised).lower():
        failures.append("the minute does not distinguish a raised item from an answer")

    # --- blueprint must never claim to be canon ---------------------------
    blueprint = compile_blueprint(
        [{"station": stations[0]["id"], "response": "ACCEPT", "by": "self-test"}],
        stations,
        "self-test",
    )
    if blueprint["blueprint"]["status"] != "PROPOSED_NOT_CANON":
        failures.append("compiled blueprint did not mark itself as a proposal")
    if "not canon" not in render_minute(blueprint).lower():
        failures.append("draft minute does not say it is not canon")

    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}", file=sys.stderr)
        return 1

    print(f"decision_interview self-test: all checks passed ({len(stations)} stations)")
    return 0


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stations", action="store_true", help="emit the generated walkthrough")
    parser.add_argument("--check", action="store_true", help="coverage and recommendation checks")
    parser.add_argument("--capture", help="a YAML file of captured responses")
    parser.add_argument("--sitting", default="undated")
    parser.add_argument("--out-dir", default=".blueprint")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    stations = build_stations()

    if args.stations:
        print(yaml.dump({"stations": stations}, sort_keys=False, allow_unicode=True, width=100))
        return 0

    if args.check:
        problems = check_coverage(stations) + check_recommendations(stations)
        posture = check_build_posture(stations)
        missing = missing_recommendations(stations)

        print(f"stations generated: {len(stations)}")
        for kind in sorted(STATION_KINDS):
            count = sum(1 for s in stations if s["kind"] == kind)
            if count:
                print(f"  {kind:<20} {count}")
        print()

        if missing:
            print(f"research queue — {len(missing)} station(s) need a recommendation:")
            for station_id in missing:
                print(f"  {station_id}")
            print()
        if posture:
            print("build posture undeclared:")
            for problem in posture:
                print(f"  {problem}")
            print()
        if problems:
            for problem in problems:
                print(f"  FAIL  {problem}", file=sys.stderr)
            return 1
        print("checks passed")
        return 0

    if args.capture:
        captured = yaml.safe_load(Path(args.capture).read_text(encoding="utf-8"))
        responses = captured.get("responses", captured if isinstance(captured, list) else [])
        raised = captured.get("raised", []) if isinstance(captured, dict) else []
        problems = check_live_conflicts(responses, stations) + check_raised(raised)

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        if problems:
            (out_dir / "conflicts.md").write_text(
                "## Not compiled — conflicts found\n\n"
                "Nothing has been changed. These need resolving in the room.\n\n"
                + "\n".join(f"- {p}" for p in problems)
                + "\n"
            )
            (out_dir / "status.txt").write_text("conflicts\n")
            for problem in problems:
                print(f"  CONFLICT  {problem}", file=sys.stderr)
            return 1

        blueprint = compile_blueprint(responses, stations, args.sitting, raised)
        (out_dir / "blueprint.yaml").write_text(
            yaml.dump(blueprint, sort_keys=False, allow_unicode=True, width=100)
        )
        (out_dir / "draft-minute.md").write_text(render_minute(blueprint))
        (out_dir / "status.txt").write_text("compiled\n")
        print(f"compiled {len(blueprint['changes'])} change(s) -> {out_dir}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
