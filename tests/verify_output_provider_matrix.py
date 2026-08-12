#!/usr/bin/env python3
"""Double-model execution, raw isolation, blind-pack, and three-reviewer gates."""

import json
import copy
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from adjudicate_multi_reviewer import adjudicate_reviews  # noqa: E402
from output_provider_matrix import build_blind_materials, execute_provider_matrix, load_provider_matrix, provider_status  # noqa: E402


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_output_provider_matrix"
    shutil.rmtree(tmp_root, ignore_errors=True)
    run_dir = tmp_root / "run"
    matrix = load_provider_matrix(ROOT / "evals" / "output" / "provider_matrix.json")
    assert [item["model"] for item in matrix["models"]] == ["deepseek-v4-flash", "deepseek-v4-pro"], matrix
    assert all(item["thinking"] == "disabled" and item["temperature"] == 0 for item in matrix["models"]), matrix
    assert matrix["limits"] == {"max_calls": 40, "max_total_tokens": 250000, "timeout_seconds": 60}, matrix
    invalid_matrix_path = tmp_root / "invalid-provider-matrix.json"
    invalid_matrix_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_matrix = copy.deepcopy(matrix)
    invalid_matrix["promotion"]["with_skill_min_wins"] = 14
    invalid_matrix_path.write_text(json.dumps(invalid_matrix), encoding="utf-8")
    try:
        load_provider_matrix(invalid_matrix_path)
    except ValueError as exc:
        assert "promotion contract" in str(exc), exc
    else:
        raise AssertionError("weakened provider promotion contract was accepted")
    readiness = provider_status(matrix)
    assert readiness["world_class_evidence"]["counts_as_completion"] is False, readiness
    readiness_text = json.dumps(readiness).lower()
    assert "authorization" not in readiness_text and "bearer " not in readiness_text, readiness

    fake_runner = ROOT / "tests" / "fixtures" / "fake_deepseek_output_runner.py"

    def runner_for(model: dict) -> list[str]:
        return [sys.executable, str(fake_runner), "--model", model["model"]]

    report = execute_provider_matrix(
        ROOT / "evals" / "output" / "holdout_cases.jsonl",
        matrix,
        run_dir,
        runner_for=runner_for,
    )
    assert report["summary"]["case_count"] == 10, report
    assert report["summary"]["call_count"] == 40, report
    assert report["summary"]["model_executed_count"] == 40, report
    assert report["summary"]["total_tokens"] == 1200, report
    assert report["summary"]["failure_count"] == 0, report
    assert report["quality_promotion"]["status"] == "awaiting-human-review", report
    assert report["world_class_evidence"]["counts_as_completion"] is False, report
    raw_files = sorted((run_dir / "raw-outputs").rglob("*.txt"))
    assert len(raw_files) == 40, raw_files
    serialized = json.dumps(report, ensure_ascii=False)
    assert "Write a short direct answer" not in serialized, report
    assert all(item["output_sha256"] and item["redacted_summary"] for item in report["runs"]), report
    assert all(not Path(item["raw_output_path"]).is_absolute() for item in report["runs"]), report

    blind_pack, answer_key, templates = build_blind_materials(report, run_dir)
    assert blind_pack["summary"]["pair_count"] == 20, blind_pack
    assert answer_key["summary"]["pair_count"] == 20, answer_key
    assert set(templates) == {"reviewer-a", "reviewer-b", "reviewer-c"}, templates
    assert all(len(template["decisions"]) == 20 for template in templates.values()), templates
    assert all("expected_winner_variant" not in json.dumps(template) for template in templates.values()), templates
    assert "Write a short direct answer" not in json.dumps(blind_pack, ensure_ascii=False), blind_pack
    assert all("variant_a" not in pair and "variant_b" not in pair for pair in blind_pack["pairs"]), blind_pack
    assert all((run_dir / pair["variant_a_raw_output"]).is_file() for pair in blind_pack["pairs"]), blind_pack
    assert all((run_dir / pair["variant_b_raw_output"]).is_file() for pair in blind_pack["pairs"]), blind_pack

    decisions = []
    for reviewer in ("reviewer-a", "reviewer-b", "reviewer-c"):
        decisions.append(
            {
                "reviewer": reviewer,
                "decisions": [
                    {
                        "pair_id": item["pair_id"],
                        "winner_variant": "A" if item["variant_a_role"] == "with_skill" else "B",
                        "critical_failure": False,
                        "reason": "The selected answer satisfies the visible rubric.",
                    }
                    for item in answer_key["answers"]
                ],
            }
        )
    adjudication = adjudicate_reviews(answer_key, decisions)
    summary = adjudication["summary"]
    assert summary["reviewer_count"] == 3, adjudication
    assert summary["with_skill_pair_wins"] == 20, adjudication
    assert summary["model_with_skill_wins"] == {"deepseek-v4-flash": 10, "deepseek-v4-pro": 10}, adjudication
    assert summary["critical_failure_count"] == 0, adjudication
    assert summary["fleiss_kappa"] == 1.0, adjudication
    assert adjudication["quality_promotion"]["eligible"] is True, adjudication
    assert adjudication["world_class_evidence"]["counts_as_completion"] is False, adjudication

    pending = adjudicate_reviews(answer_key, decisions[:2])
    assert pending["quality_promotion"]["status"] == "pending", pending
    assert pending["quality_promotion"]["eligible"] is False, pending

    limited_matrix = copy.deepcopy(matrix)
    limited_matrix["limits"]["max_calls"] = 1
    limited = execute_provider_matrix(
        ROOT / "evals" / "output" / "holdout_cases.jsonl",
        limited_matrix,
        tmp_root / "limited-run",
        runner_for=runner_for,
    )
    assert limited["summary"]["call_count"] == 1, limited
    assert limited["summary"]["failure_count"] == 1, limited
    assert any(not item["command_executed"] and "budget exhausted" in item["failure"] for item in limited["runs"]), limited
    try:
        build_blind_materials(limited, tmp_root / "limited-run")
    except ValueError as exc:
        assert "40 successful" in str(exc), exc
    else:
        raise AssertionError("partial provider run produced blind materials")

    print(json.dumps({"ok": True}, indent=2))


if __name__ == "__main__":
    main()
