PYTHON ?= python3

.PHONY: eval eval-suite results-panel regression-history failure-regression-check package-check package-failure-check snapshot-check validate lint governance-check resource-boundary-check quality-check test clean

eval:
	$(PYTHON) scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json --baseline-description-file evals/baseline_description.txt

eval-suite:
	$(PYTHON) scripts/run_eval_suite.py

results-panel:
	$(PYTHON) scripts/render_eval_dashboard.py

regression-history:
	$(PYTHON) scripts/render_regression_history.py

failure-regression-check:
	$(PYTHON) tests/verify_failure_regressions.py

package-check:
	$(PYTHON) scripts/cross_packager.py . --platform openai --platform claude --platform generic --expectations evals/packaging_expectations.json --output-dir dist --zip

package-failure-check:
	$(PYTHON) tests/verify_packager_failures.py

snapshot-check:
	$(PYTHON) tests/verify_adapter_snapshots.py

validate:
	$(PYTHON) scripts/validate_skill.py .

lint:
	$(PYTHON) scripts/lint_skill.py .

governance-check:
	$(PYTHON) scripts/governance_check.py . --require-manifest

resource-boundary-check:
	$(PYTHON) scripts/resource_boundary_check.py .

quality-check:
	$(PYTHON) tests/verify_quality_checks.py

test: eval eval-suite regression-history failure-regression-check package-check package-failure-check snapshot-check validate lint governance-check resource-boundary-check quality-check

clean:
	rm -rf dist tests/tmp tests/tmp_snapshot
