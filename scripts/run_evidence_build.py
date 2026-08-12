#!/usr/bin/env python3
"""Build an isolated evidence run and optionally publish it transactionally."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from evidence_store import EvidenceError, EvidenceStore
from output_provider_matrix import build_blind_materials, execute_provider_matrix, load_provider_matrix, provider_status


ROOT = Path(__file__).resolve().parent.parent


def provider_evidence(store: EvidenceStore, run, skill_dir: Path):
    matrix_path = skill_dir / "evals" / "output" / "provider_matrix.json"
    cases_path = skill_dir / "evals" / "output" / "holdout_cases.jsonl"
    if not matrix_path.exists() or not cases_path.exists():
        return run, {"status": "not-configured", "quality_promotion": {"status": "pending", "eligible": False}}
    matrix = load_provider_matrix(matrix_path)
    api_key_env = str(matrix["api_key_env"])
    if not os.environ.get(api_key_env):
        status = provider_status(matrix)
        return store.add_json_artifact(run, "reports/provider_output_evaluation.json", status), status
    report = execute_provider_matrix(cases_path, matrix, run.run_dir)
    artifacts = [("reports/provider_output_evaluation.json", report)]
    if report.get("summary", {}).get("failure_count") == 0 and len(report.get("runs", [])) == 40:
        blind_pack, answer_key, templates = build_blind_materials(report, run.run_dir)
        artifacts.extend(
            [
                ("reports/provider_output_blind_pack.json", blind_pack),
                ("reports/provider_output_answer_key.json", answer_key),
                ("reports/provider_review_reviewer-a.json", templates["reviewer-a"]),
                ("reports/provider_review_reviewer-b.json", templates["reviewer-b"]),
                ("reports/provider_review_reviewer-c.json", templates["reviewer-c"]),
            ]
        )
    for relative, payload in artifacts:
        run = store.add_json_artifact(run, relative, payload)
    return run, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build isolated, hash-indexed evidence for an agent skill.")
    parser.add_argument("skill_dir")
    parser.add_argument("--run-id")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    try:
        store = EvidenceStore(Path(args.skill_dir))
        recovered = store.recover()
        if args.publish:
            store.assert_clean()
        run = store.build(args.run_id)
        run, provider = provider_evidence(store, run, store.skill_dir)
        release = store.publish(run) if args.publish else None
        payload = {
            "ok": True,
            "mode": "published" if release else "dry-run",
            "run_id": run.run_id,
            "skill_name": run.manifest["skill_name"],
            "run_dir": str(run.run_dir),
            "artifact_count": run.manifest["artifact_count"],
            "provider_evidence_status": provider.get("status", provider.get("quality_promotion", {}).get("status", "pending")),
            "release_dir": str(release) if release else None,
            "recovered_previous_publish": recovered,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except EvidenceError as exc:
        print(
            json.dumps(
                {"ok": False, "error": {"code": exc.code, "message": str(exc)}},
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
