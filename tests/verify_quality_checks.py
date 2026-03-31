#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(name: str, cmd: list[str], expect_ok: bool = True, expected_substrings: list[str] | None = None) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = {}
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = {"raw_stdout": proc.stdout}

    joined = proc.stdout + "\n" + proc.stderr
    passed = proc.returncode == 0 if expect_ok else proc.returncode == 2
    if expected_substrings:
        passed = passed and all(fragment in joined for fragment in expected_substrings)

    return {
        "name": name,
        "passed": passed,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "payload": payload,
    }


def require_min_score(case: dict, minimum: int) -> None:
    score = case.get("payload", {}).get("details", {}).get("governance_score")
    case["minimum_score"] = minimum
    case["observed_score"] = score
    case["passed"] = case["passed"] and score is not None and score >= minimum


def main() -> None:
    python = sys.executable
    cases = []

    root_governance = run(
            "root_governance",
            [python, "scripts/governance_check.py", str(ROOT), "--require-manifest"],
        )
    require_min_score(root_governance, 90)
    cases.append(root_governance)

    cases.extend([
        run(
            "root_resource_boundaries",
            [python, "scripts/resource_boundary_check.py", str(ROOT)],
        ),
        run(
            "complex_example_governance",
            [python, "scripts/governance_check.py", str(ROOT / "examples" / "complex-release-orchestrator" / "generated-skill"), "--require-manifest"],
        ),
        run(
            "complex_example_resource_boundaries",
            [python, "scripts/resource_boundary_check.py", str(ROOT / "examples" / "complex-release-orchestrator" / "generated-skill")],
        ),
        run(
            "governed_example_resource_boundaries",
            [python, "scripts/resource_boundary_check.py", str(ROOT / "examples" / "governed-incident-command" / "generated-skill")],
        ),
        run(
            "invalid_governance_manifest",
            [python, "scripts/governance_check.py", str(ROOT / "tests" / "fixtures" / "governance_invalid_manifest"), "--require-manifest"],
            expect_ok=False,
            expected_substrings=[
                "Missing manifest fields",
                "Invalid status",
                "updated_at must use YYYY-MM-DD",
                "manifest name does not match",
            ],
        ),
    ])

    governed_example = run(
        "governed_example_governance",
        [python, "scripts/governance_check.py", str(ROOT / "examples" / "governed-incident-command" / "generated-skill"), "--require-manifest"],
    )
    require_min_score(governed_example, 90)
    cases.insert(4, governed_example)

    report = {"ok": all(case["passed"] for case in cases), "cases": cases}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
