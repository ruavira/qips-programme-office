#!/usr/bin/env python3
"""Generate the file-level inventory of active workstream working artifacts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "governance/ikr-pos/registers/workstream-artifacts.yaml"


def title_for(path: Path) -> str:
    if path.suffix.lower() == ".md":
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def authority_for(name: str) -> str:
    lowered = name.lower()
    if "dossier" in lowered:
        return "PROPOSED"
    if "evidence-register" in lowered or "research" in lowered:
        return "EVIDENCE_SUPPORTED"
    if "verification" in lowered or "council-record" in lowered:
        return "DERIVED"
    return "PROPOSED"


def artifact_type_for(name: str) -> str:
    lowered = name.lower()
    if "evidence-register" in lowered:
        return "EVIDENCE_REGISTER"
    if "verification" in lowered:
        return "VERIFICATION_RECORD"
    if "council-record" in lowered:
        return "COUNCIL_RECORD"
    if "dossier" in lowered:
        return "DRAFT_DOSSIER"
    if name.endswith((".mjs", ".js", ".py")):
        return "WORKING_TOOL"
    return "WORKING_ARTIFACT"


def build_inventory(source_revision: str) -> dict:
    artifacts = []
    paths = sorted(ROOT.glob("workstreams/W*/working/*"))
    for path in paths:
        if not path.is_file() or path.name == ".keep":
            continue
        relative = path.relative_to(ROOT).as_posix()
        owner = path.parts[-3]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        stable_id = hashlib.sha1(relative.encode("utf-8")).hexdigest()[:8].upper()
        artifacts.append(
            {
                "id": f"ART-{owner}-{stable_id}",
                "title": title_for(path),
                "owner": owner,
                "path": relative,
                "artifact_type": artifact_type_for(path.name),
                "lifecycle_status": "DRAFT",
                "authority_class": authority_for(path.name),
                "confidentiality": "PROGRAMME",
                "version": "git",
                "sha256": digest,
                "review_requirement": "WORKSTREAM_REVIEW_AND_CCC_IF_PROMOTED",
            }
        )
    return {
        "register": {
            "id": "QIPS-WAIR",
            "title": "QIPS Workstream Active Artifact Inventory",
            "version": "1.0.0",
            "owner": "W09",
            "assurance_owner": "W11",
            "status": "ACTIVE",
            "generated_on": "2026-08-13",
            "source_revision": source_revision,
            "coverage": "workstreams/W01-W17/working excluding .keep files",
            "artifact_count": len(artifacts),
        },
        "artifacts": artifacts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()
    payload = build_inventory(args.source_revision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=110),
        encoding="utf-8",
    )
    print(f"artifact inventory: {args.output} ({payload['register']['artifact_count']} files)")


if __name__ == "__main__":
    main()
