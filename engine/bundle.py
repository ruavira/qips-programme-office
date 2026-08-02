#!/usr/bin/env python3
"""Build an apply bundle, and refuse to emit one that has not been proved to work.

WHY THIS EXISTS
---------------
Three times in this project an agent handed the programme director a command that
had never been run:

  - a path under ~/Downloads that had never been written, because delivering a file
    to a chat is not the same as writing it to a disk;
  - an APPLY script carrying backticks inside a double-quoted --body, so bash
    performed command substitution and mangled the pull request text;
  - a FIX script targeting a branch that had already merged, which would have
    pushed to a dead ref and *appeared* to succeed.

All three were the same failure: asserting instead of checking. The director's
standing instruction is "always do your due diligence before asking me to do
things." A rule in prose does not enforce itself. This does.

THE STANDARD
------------
No bundle is delivered until the exact script the human will run has been run
here, against a FRESH CLONE of the repository, with `git push` stubbed. Every gate
must pass. If the dry run fails, no bundle is emitted at all — there is nothing to
hand over and nothing to be tempted by.

The bundle carries a MANIFEST recording what was proved: the base commit, the
files touched, every gate and its exit code, and the dry-run verdict. The manifest
is the receipt. A bundle without a green manifest is not a bundle.

Usage:
    python3 engine/bundle.py --branch proposal/foo --number 14 --out ~/bundles
    python3 engine/bundle.py --verify ~/bundles/14_FOO      # re-prove an old bundle
    python3 engine/bundle.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# The gates every bundle must clear before it may be handed to a human. Explicit
# rather than discovered, so that adding a gate is a reviewable change.
GATES: list[list[str]] = [
    ["python3", "engine/validate_ikr_pos.py"],
    ["python3", "engine/curriculum.py"],
    ["python3", "engine/admissions.py"],
    ["python3", "engine/decision_capture.py", "--self-test"],
    ["python3", "engine/decision_interview.py", "--self-test"],
    ["python3", "engine/decision_interview.py", "--check"],
]

REMOTE = "https://github.com/ruavira/qips-programme-office.git"

# Patterns that have actually broken a delivered script. Checked before the dry
# run, because a static catch gives a better error than a mangled push.
SCRIPT_SMELLS: list[tuple[str, str]] = [
    (
        r'--body\s+"[^"]*`',
        "backticks inside a double-quoted --body: bash will perform command "
        "substitution and mangle the text. Use a heredoc or single quotes.",
    ),
    (
        r"\bgh\s+pr\s+create\b",
        "gh pr create in an apply script: proposal.yml opens the PR on push. "
        "Calling it here races the workflow and produces duplicates.",
    ),
    (
        r"\bgit\s+apply\s+-3\b",
        "git apply -3 silently drops content — it reports 'applied with conflicts, "
        "falling back to direct application' with no markers. Use git am.",
    ),
    (
        r"\bgit\s+push\b.*\bmain\b",
        "a push to main: canon is only written by a merged pull request.",
    ),
]


class BundleError(Exception):
    """The bundle cannot be built or cannot be proved. Nothing is emitted."""


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        env={**os.environ, **(env or {})},
    )
    return proc.returncode, (proc.stdout + proc.stderr)


# ---------------------------------------------------------------------------

def strip_comments(script: str) -> str:
    """Drop whole-line shell comments before smell-checking.

    Without this the checker flags its own template, which documents in a comment
    that it does NOT call `gh pr create`. Caught by the self-test on first run —
    which is the argument for having one.
    """
    return "\n".join(
        line for line in script.splitlines() if not line.lstrip().startswith("#")
    )


def check_script_smells(script: str) -> list[str]:
    """Static checks for the specific ways delivered scripts have broken before."""
    executable = strip_comments(script)
    return [
        message
        for pattern, message in SCRIPT_SMELLS
        if re.search(pattern, executable, re.IGNORECASE)
    ]


def gate_script(gate: list[str]) -> str:
    """The file a gate runs, so its presence can be tested before running it."""
    return gate[1]


def render_gate(gate: list[str]) -> str:
    """A gate, guarded by whether it exists at this base.

    A bundle cut against main cannot run a validator that main does not yet have —
    that is how this function came to exist, when the prover refused its own first
    bundle. The skip is LOUD and lands in the manifest: a gate that quietly did not
    run reads as a gate that passed, which is the failure this whole module exists
    to prevent.
    """
    path = gate_script(gate)
    return (
        f'if [ -f "{path}" ]; then\n'
        f"  {shell_join(gate)}\n"
        f"else\n"
        f'  echo "   SKIP  {path} is not present at this base — gate not run"\n'
        f"fi"
    )


def render_apply_script(
    branch: str, patches: list[str], title: str, expected_tree: str, base_is_remote: bool
) -> str:
    gate_lines = "\n".join(render_gate(gate) for gate in GATES)
    patch_lines = "\n".join(
        f'git am --keep-cr "$HERE/{name}"' for name in patches
    )
    base_note = (
        "cut against the CURRENT REMOTE TIP of this branch, so applying it is a "
        "fast-forward and no force push is ever needed"
        if base_is_remote
        else "cut against main, because this branch does not exist on the remote yet"
    )
    return f"""#!/usr/bin/env bash
# {title}
#
# Proved before delivery: this exact script was run TWICE against a fresh clone
# with git push stubbed, and every gate passed both times. See MANIFEST.json.
#
# This bundle is {base_note}.
#
# Pushes a proposal/** branch. .github/workflows/proposal.yml opens the pull
# request itself -- no gh pr create here, and none is needed.
set -euo pipefail

REPO="${{1:?usage: bash $(basename "$0") /path/to/qips-programme-office}}"
HERE="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
BRANCH="{branch}"

# The exact tree this bundle promises to produce. Checked after applying, so the
# script proves it built what it said it would rather than assuming it did.
EXPECTED_TREE="{expected_tree}"

cd "$REPO"
echo "==> repo: $(pwd)"
git remote -v | head -1

git fetch origin main

echo "==> checking whether this branch already exists on the remote"
if git ls-remote --heads origin "$BRANCH" | grep -q "refs/heads/$BRANCH$"; then
  git fetch -q origin "$BRANCH"

  # Re-running a delivered bundle must be safe. `git am` regenerates the commit
  # with a new timestamp, so a naive re-run produces a SIBLING of what was pushed
  # and the push is rejected as non-fast-forward -- confusing, and it looks like
  # breakage when nothing is broken.
  if [ "$(git rev-parse FETCH_HEAD^{{tree}})" = "$EXPECTED_TREE" ]; then
    echo
    echo "Already delivered. origin/$BRANCH already carries exactly this content."
    echo "Nothing pushed, nothing changed. Re-running this script is always safe."
    git checkout -q -B "$BRANCH" FETCH_HEAD
    echo "Local branch realigned to the remote."
    exit 0
  fi

  echo "==> branch exists on the remote; building on top of it (fast-forward)"
  git checkout -q -B "$BRANCH" FETCH_HEAD
else
  echo "==> branch is new; building from main"
  git checkout -q main
  git pull --ff-only origin main
  git checkout -q -B "$BRANCH" main
fi

echo "==> applying patch series"
{patch_lines}

echo "==> confirming the applied tree is the one this bundle promised"
ACTUAL_TREE="$(git rev-parse HEAD^{{tree}})"
if [ "$ACTUAL_TREE" != "$EXPECTED_TREE" ]; then
  echo
  echo "STOP. The applied content does not match what this bundle promised."
  echo "  expected tree: $EXPECTED_TREE"
  echo "  actual tree:   $ACTUAL_TREE"
  echo "Nothing has been pushed. Re-prove the bundle before using it:"
  echo "  python3 engine/bundle.py --verify <bundle-dir>"
  exit 1
fi
echo "    ok    tree matches $EXPECTED_TREE"

echo "==> verifying before push (never push a red engine)"
{gate_lines}

echo "==> pushing"
git push -u origin "$BRANCH"

echo
echo "Pushed $BRANCH."
echo "The proposal workflow opens the pull request. Watch it here:"
echo "  https://github.com/ruavira/qips-programme-office/actions"
echo "  https://github.com/ruavira/qips-programme-office/pulls"
"""


def shell_join(cmd: list[str]) -> str:
    return " ".join(cmd)


# ---------------------------------------------------------------------------

def dry_run(bundle_dir: Path, script_name: str) -> dict[str, Any]:
    """Run the human's exact script against a fresh clone, with push stubbed.

    A fresh clone, not the working copy: a script that only works because of local
    state is a script that will fail on the director's machine.
    """
    result: dict[str, Any] = {"passed": False, "steps": [], "log_tail": ""}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        clone = tmp_path / "clone"
        stub = tmp_path / "stub"
        stub.mkdir()

        # A git shim that refuses to push but is otherwise the real git. It records
        # what WOULD have been pushed, so the dry run still proves the ref.
        real_git = shutil.which("git")
        if not real_git:
            raise BundleError("git is not on PATH; the dry run cannot be trusted.")
        pushlog = tmp_path / "push.log"
        # The stub is not merely a push blocker. It REMEMBERS what was pushed and
        # reports it back through ls-remote and fetch, so a second run of the
        # script sees the same world a human's second run would see. Without that,
        # the dry run could never exercise the already-delivered path — and the
        # already-delivered path is exactly where the real defect was.
        (stub / "git").write_text(
            f"""#!/bin/sh
REAL="{real_git}"
STATE="{pushlog}"
case "$1" in
  push)
    for a in "$@"; do last="$a"; done
    sha=$("$REAL" rev-parse "$last" 2>/dev/null)
    printf '%s\\trefs/heads/%s\\n' "$sha" "$last" >> "$STATE"
    echo "[dry-run] git push $* -> $sha"
    exit 0 ;;
  ls-remote)
    "$REAL" "$@"
    if [ -f "$STATE" ]; then
      for a in "$@"; do grep "refs/heads/$a$" "$STATE" 2>/dev/null; done
    fi
    exit 0 ;;
  fetch)
    for a in "$@"; do last="$a"; done
    if [ -f "$STATE" ] && grep -q "refs/heads/$last$" "$STATE"; then
      sha=$(grep "refs/heads/$last$" "$STATE" | tail -1 | cut -f1)
      "$REAL" update-ref FETCH_HEAD "$sha"
      echo "[dry-run] git fetch $* -> $sha"
      exit 0
    fi
    exec "$REAL" "$@" ;;
esac
exec "$REAL" "$@"
"""
        )
        (stub / "git").chmod(0o755)

        code, out = _run([real_git, "clone", "--quiet", REMOTE, str(clone)], tmp_path)
        result["steps"].append({"step": "clone", "exit": code})
        if code != 0:
            result["log_tail"] = out[-2000:]
            return result

        stub_env = {"PATH": f"{stub}:{os.environ.get('PATH', '')}"}

        # RUN 1 — the first delivery.
        code, out = _run(["bash", str(bundle_dir / script_name), str(clone)], clone, stub_env)
        result["steps"].append({"step": "apply-script (run 1)", "exit": code})
        result["log_tail"] = out[-4000:]
        if code != 0:
            return result

        if not pushlog.is_file():
            result["steps"].append(
                {"step": "push-reached", "exit": 1, "note": "the script never reached a push"}
            )
            return result
        result["pushed_ref"] = pushlog.read_text().strip()

        # RUN 2 — the human re-runs the same command, as humans do. This must be
        # safe. It was not, until a real second run rejected as non-fast-forward
        # on 2026-08-02, which the single-run dry run had no way of catching.
        code, out = _run(["bash", str(bundle_dir / script_name), str(clone)], clone, stub_env)
        result["steps"].append({"step": "apply-script (run 2, idempotency)", "exit": code})
        if code != 0:
            result["log_tail"] = out[-4000:]
            result["steps"].append(
                {
                    "step": "idempotency",
                    "exit": 1,
                    "note": "re-running the delivered script is not safe",
                }
            )
            return result
        if "Already delivered" not in out:
            result["steps"].append(
                {
                    "step": "idempotency",
                    "exit": 1,
                    "note": "the second run did not recognise the branch as already delivered",
                }
            )
            return result
        result["idempotent"] = True

        # Re-run every gate directly in the clone, so a gate that the script
        # skipped or swallowed cannot pass unnoticed. A gate whose script does not
        # exist at this base is recorded as SKIPPED, never as passed.
        ran = 0
        for gate in GATES:
            if not (clone / gate_script(gate)).is_file():
                result["steps"].append(
                    {
                        "step": shell_join(gate),
                        "exit": None,
                        "skipped": "script not present at this base",
                    }
                )
                continue
            code, out = _run(gate, clone)
            result["steps"].append({"step": shell_join(gate), "exit": code})
            ran += 1
            if code != 0:
                result["log_tail"] = out[-4000:]
                return result

        result["gates_run"] = ran
        result["gates_skipped"] = [
            s["step"] for s in result["steps"] if s.get("skipped")
        ]
        if ran == 0:
            result["steps"].append(
                {"step": "gates", "exit": 1, "note": "no gate ran at all"}
            )
            return result

    result["passed"] = True
    return result


# ---------------------------------------------------------------------------

def build(branch: str, number: int, slug: str, out_root: Path, title: str) -> Path:
    code, out = _run(["git", "rev-parse", "--verify", branch], ROOT)
    if code != 0:
        raise BundleError(f"branch {branch} does not exist locally.")

    expected_tree = _run(["git", "rev-parse", f"{branch}^{{tree}}"], ROOT)[1].strip()

    # Cut against the REMOTE TIP when the branch is already published. A bundle
    # cut against main can never fast-forward a branch that has already been
    # pushed -- `git am` regenerates commits, so re-applying from main produces a
    # sibling history and the push is rejected. Found on 2026-08-02 when the
    # director re-ran a delivered script. Cutting from the remote tip means an
    # update is always a fast-forward and a force push is never needed.
    code, remote_out = _run(["git", "ls-remote", "--heads", "origin", branch], ROOT)
    remote_tip = remote_out.split()[0] if code == 0 and remote_out.strip() else None
    base_is_remote = False

    if remote_tip:
        _run(["git", "fetch", "-q", "origin", branch], ROOT)
        remote_tree = _run(["git", "rev-parse", f"{remote_tip}^{{tree}}"], ROOT)[1].strip()
        if remote_tree == expected_tree:
            raise BundleError(
                f"nothing to deliver: origin/{branch} already carries exactly this content "
                f"({remote_tip[:12]}). There is no bundle to build."
            )
        code, _ = _run(["git", "merge-base", "--is-ancestor", remote_tip, branch], ROOT)
        if code == 0:
            base, base_is_remote = remote_tip, True
        else:
            raise BundleError(
                f"origin/{branch} ({remote_tip[:12]}) is not an ancestor of the local branch, so "
                "an update cannot fast-forward. Rebase the local branch onto the remote tip "
                f"first:\n    git fetch origin {branch} && git rebase FETCH_HEAD {branch}"
            )
    else:
        code, base = _run(["git", "merge-base", "origin/main", branch], ROOT)
        if code != 0:
            raise BundleError("could not find a merge base with origin/main.")
        base = base.strip()

    code, changed = _run(["git", "diff", "--name-only", f"{base}..{branch}"], ROOT)
    files = [line for line in changed.splitlines() if line.strip()]
    if not files:
        raise BundleError(f"{branch} changes nothing against its base.")

    bundle_dir = out_root / f"{number:02d}_{slug}"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)

    code, out = _run(
        ["git", "format-patch", f"{base}..{branch}", "-o", str(bundle_dir)], ROOT
    )
    if code != 0:
        raise BundleError(f"format-patch failed:\n{out}")
    patches = sorted(p.name for p in bundle_dir.glob("*.patch"))
    if not patches:
        raise BundleError("format-patch produced no patches.")

    script_name = f"APPLY-{number}.sh"
    script = render_apply_script(branch, patches, title, expected_tree, base_is_remote)

    smells = check_script_smells(script)
    if smells:
        shutil.rmtree(bundle_dir)
        raise BundleError(
            "the generated script contains known-bad patterns; nothing emitted:\n  - "
            + "\n  - ".join(smells)
        )

    (bundle_dir / script_name).write_text(script)
    (bundle_dir / script_name).chmod(0o755)

    print(f"==> built {bundle_dir.name}; proving it before it may be delivered")
    proof = dry_run(bundle_dir, script_name)

    manifest = {
        "bundle": bundle_dir.name,
        "title": title,
        "branch": branch,
        "base_commit": base,
        "base_is_remote_tip": base_is_remote,
        "expected_tree": expected_tree,
        "patches": patches,
        "files_changed": files,
        "gates": [shell_join(g) for g in GATES],
        "dry_run": proof,
        "delivery_rule": (
            "This bundle was proved by running the exact script above against a fresh "
            "clone of the repository with git push stubbed. Every gate passed. A bundle "
            "whose manifest does not say dry_run.passed = true must not be delivered."
        ),
    }

    if not proof["passed"]:
        (bundle_dir / "FAILED-MANIFEST.json").write_text(json.dumps(manifest, indent=2))
        failed = bundle_dir.with_name(bundle_dir.name + "-FAILED")
        if failed.exists():
            shutil.rmtree(failed)
        bundle_dir.rename(failed)
        raise BundleError(
            f"dry run FAILED; nothing deliverable was emitted.\n"
            f"Diagnostics kept at {failed}\n\n"
            + proof["log_tail"][-1500:]
        )

    (bundle_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"==> dry run passed; {bundle_dir.name} may be delivered")
    return bundle_dir


def verify(bundle_dir: Path) -> int:
    """Re-prove a bundle that already exists. Bundles go stale."""
    manifest_path = bundle_dir / "MANIFEST.json"
    if not manifest_path.is_file():
        print(f"  FAIL  {bundle_dir} has no MANIFEST.json — it was never proved.", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text())

    scripts = sorted(bundle_dir.glob("APPLY-*.sh"))
    if len(scripts) != 1:
        print(f"  FAIL  expected exactly one APPLY script, found {len(scripts)}", file=sys.stderr)
        return 1

    smells = check_script_smells(scripts[0].read_text())
    for smell in smells:
        print(f"  FAIL  {smell}", file=sys.stderr)

    proof = dry_run(bundle_dir, scripts[0].name)
    manifest["dry_run"] = proof
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    if smells or not proof["passed"]:
        print(f"  FAIL  {bundle_dir.name} no longer applies cleanly. Do not deliver it.",
              file=sys.stderr)
        print(proof["log_tail"][-1200:], file=sys.stderr)
        return 1
    print(f"{bundle_dir.name}: re-proved, still good")
    return 0


# ---------------------------------------------------------------------------

def self_test() -> int:
    failures: list[str] = []

    # every pattern that has bitten before must still be caught
    cases = [
        ('gh pr create --body "see `git log`"', "backticks"),
        ("gh pr create --title x", "gh pr create"),
        ("git apply -3 foo.patch", "git apply -3"),
        ("git push origin main", "push to main"),
    ]
    for script, label in cases:
        if not check_script_smells(script):
            failures.append(f"{label!r} was not caught by check_script_smells")

    clean = render_apply_script("proposal/x", ["0001-x.patch"], "test", "deadbeef", False)
    if check_script_smells(clean):
        failures.append(f"a clean generated script was flagged: {check_script_smells(clean)}")

    # the generated script must run every gate, and must guard each one, and the
    # skip must be loud — a silent skip reads as a pass
    for gate in GATES:
        if shell_join(gate) not in clean:
            failures.append(f"generated script omits gate: {shell_join(gate)}")
        if f'if [ -f "{gate_script(gate)}" ]' not in clean:
            failures.append(f"gate not guarded for existence: {gate_script(gate)}")
    if clean.count("SKIP") != len(GATES):
        failures.append("not every gate announces its skip")

    # re-running a delivered bundle must be recognised, never forced
    if "Already delivered" not in clean:
        failures.append("generated script has no already-delivered path; a re-run will fail")
    if "ls-remote" not in clean:
        failures.append("generated script does not check the remote before pushing")
    if "--force" in clean:
        failures.append("generated script force-pushes; it must stop and explain instead")
    if "set -euo pipefail" not in clean:
        failures.append("generated script does not fail fast")
    if "git push -u origin" not in clean:
        failures.append("generated script never pushes")

    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}", file=sys.stderr)
        return 1
    print("bundle self-test: all checks passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch")
    parser.add_argument("--number", type=int)
    parser.add_argument("--slug", help="folder suffix, e.g. CCC_INTERVIEW")
    parser.add_argument("--title", default="")
    parser.add_argument("--out", default=str(Path.home() / "bundles"))
    parser.add_argument("--verify", help="path to an existing bundle to re-prove")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.verify:
        return verify(Path(args.verify).expanduser())

    if not (args.branch and args.number and args.slug):
        parser.error("--branch, --number and --slug are required")

    try:
        bundle_dir = build(
            args.branch, args.number, args.slug,
            Path(args.out).expanduser(),
            args.title or args.branch,
        )
    except BundleError as exc:
        print(f"\nbundle: {exc}", file=sys.stderr)
        return 1

    print(f"\n{bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
