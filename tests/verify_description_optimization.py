#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


CASES = [
    {
        "name": "root",
        "description_file": ROOT / "SKILL.md",
        "baseline_description_file": ROOT / "evals" / "baseline_description.txt",
        "semantic_config": ROOT / "evals" / "semantic_config.json",
        "dev_cases": ROOT / "evals" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "evals" / "holdout" / "trigger_cases.json",
        "blind_holdout_cases": ROOT / "evals" / "blind_holdout" / "trigger_cases.json",
    },
    {
        "name": "team_frontend_review",
        "description_file": ROOT / "examples" / "team-frontend-review" / "generated-skill" / "SKILL.md",
        "baseline_description_file": ROOT / "examples" / "team-frontend-review" / "optimization" / "baseline_description.txt",
        "semantic_config": ROOT / "examples" / "team-frontend-review" / "optimization" / "semantic_config.json",
        "dev_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "holdout" / "trigger_cases.json",
        "blind_holdout_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "blind_holdout" / "trigger_cases.json",
    },
    {
        "name": "governed_incident_command",
        "description_file": ROOT / "examples" / "governed-incident-command" / "generated-skill" / "SKILL.md",
        "baseline_description_file": ROOT / "examples" / "governed-incident-command" / "optimization" / "baseline_description.txt",
        "semantic_config": ROOT / "examples" / "governed-incident-command" / "optimization" / "semantic_config.json",
        "dev_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "holdout" / "trigger_cases.json",
        "blind_holdout_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "blind_holdout" / "trigger_cases.json",
    },
]


def total_errors(summary: dict) -> int:
    return int(summary.get("false_positives", 0)) + int(summary.get("false_negatives", 0))


def run_case(case: dict) -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/optimize_description.py",
            "--description-file",
            str(case["description_file"]),
            "--baseline-description-file",
            str(case["baseline_description_file"]),
            "--semantic-config",
            str(case["semantic_config"]),
            "--dev-cases",
            str(case["dev_cases"]),
            "--holdout-cases",
            str(case["holdout_cases"]),
            "--blind-holdout-cases",
            str(case["blind_holdout_cases"]),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    current = payload["current_candidate"]
    winner = payload["winner"]
    baseline = payload.get("baseline")
    passed = proc.returncode == 0
    passed = passed and total_errors(winner["dev"]) <= total_errors(current["dev"])
    passed = passed and total_errors(winner["holdout"]) <= total_errors(current["holdout"])
    if baseline:
        passed = passed and total_errors(winner["dev"]) <= total_errors(baseline["dev"])
        passed = passed and total_errors(winner["holdout"]) <= total_errors(baseline["holdout"])
    blind_winner = payload["acceptance_gates"]["blind_holdout_non_regression"]["winner"]
    blind_current = payload["acceptance_gates"]["blind_holdout_non_regression"]["current"]
    blind_baseline = payload["acceptance_gates"]["blind_holdout_non_regression"]["baseline"]
    passed = passed and blind_winner is not None and total_errors(blind_winner) <= total_errors(blind_current)
    if blind_baseline:
        passed = passed and total_errors(blind_winner) <= total_errors(blind_baseline)
    passed = passed and len(payload.get("candidates", [])) >= 3
    return {
        "name": case["name"],
        "passed": passed,
        "returncode": proc.returncode,
        "summary": payload["summary"],
        "winner_label": winner["label"],
        "winner_tokens": winner["estimated_tokens"],
        "current_tokens": current["estimated_tokens"],
        "baseline_tokens": baseline["estimated_tokens"] if baseline else None,
        "winner_blind_holdout_total_errors": total_errors(blind_winner) if blind_winner else None,
    }


def main() -> None:
    results = [run_case(case) for case in CASES]
    report = {"ok": all(result["passed"] for result in results), "cases": results}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
