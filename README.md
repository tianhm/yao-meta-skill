# Yao Meta Skill

[![English](https://img.shields.io/badge/Docs-English-black)](README.md)
[![中文](https://img.shields.io/badge/Docs-%E4%B8%AD%E6%96%87-red)](docs/README.zh-CN.md)
[![日本語](https://img.shields.io/badge/Docs-%E6%97%A5%E6%9C%AC%E8%AA%9E-blue)](docs/README.ja-JP.md)
[![Français](https://img.shields.io/badge/Docs-Fran%C3%A7ais-green)](docs/README.fr-FR.md)
[![Русский](https://img.shields.io/badge/Docs-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-purple)](docs/README.ru-RU.md)

`yao-meta-skill` is a meta-skill for building other agent skills.

It turns rough workflows, transcripts, prompts, notes, and runbooks into reusable skill packages with:

- a clear trigger surface
- a lean `SKILL.md`
- optional references, scripts, and evals
- neutral source metadata plus client-specific adapters

## Quick Start

1. Describe the workflow, prompt set, or repeated task you want to turn into a skill.
2. Use `yao-meta-skill` to generate or improve the package in scaffold, production, or library mode.
3. Run `context_sizer.py`, `trigger_eval.py`, and `cross_packager.py` as needed to validate and export the result.

## 5-Minute Workflow

1. Start from a raw workflow note.
2. Turn it into a skill package with `SKILL.md`, `agents/interface.yaml`, and only the folders the workflow actually needs.
3. Validate the trigger description with `evals/trigger_cases.json`.
4. Export compatibility artifacts for the clients you care about.
5. Compare the result against the examples in `examples/`.

Minimum commands:

```bash
python3 scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json
python3 scripts/context_sizer.py .
python3 scripts/cross_packager.py . --platform openai --platform claude --platform generic --expectations evals/packaging_expectations.json --zip
python3 tests/verify_packager_failures.py
```

Or run everything together:

```bash
make test
```

## Results

The homepage panel below is generated from the current eval suite so the family-level outcome is visible without opening raw JSON.

<!-- BEGIN:EVAL_RESULTS -->
- regression corpus: `66` prompts across `21` families
- aggregate result: `0` false positives, `0` false negatives, average precision `1.0`, average recall `1.0`
- suite status:

| Suite | Cases | FP | FN | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 31 | 0 | 0 | 1.0 | 1.0 |
| dev | 22 | 0 | 0 | 1.0 | 1.0 |
| holdout | 13 | 0 | 0 | 1.0 | 1.0 |

| Family | Cases | Pass Rate |
| --- | ---: | ---: |
| `brainstorm_only` | 2 | 1.0 |
| `brainstorm_vs_build` | 1 | 1.0 |
| `complex_multi_asset` | 3 | 1.0 |
| `document_export_vs_agent_skill` | 4 | 1.0 |
| `document_only` | 3 | 1.0 |
| `explain_not_package` | 1 | 1.0 |
| `explain_only` | 5 | 1.0 |
| `future_outline_vs_build` | 4 | 1.0 |
| `iterate_existing_skill` | 5 | 1.0 |
| `long_context_document_only` | 3 | 1.0 |
| `long_context_near_neighbor` | 3 | 1.0 |
| `long_context_summary_only` | 2 | 1.0 |
| `long_context_trigger` | 4 | 1.0 |
| `meta_skill_creation` | 1 | 1.0 |
| `one_off_vs_reusable` | 2 | 1.0 |
| `package_for_team` | 2 | 1.0 |
| `paraphrase_trigger` | 5 | 1.0 |
| `partial_scaffold_not_full_skill` | 4 | 1.0 |
| `summary_only` | 3 | 1.0 |
| `translate_only` | 4 | 1.0 |
| `workflow_to_skill` | 5 | 1.0 |

Full reports: [reports/eval_suite.json](reports/eval_suite.json) and [reports/family_summary.md](reports/family_summary.md)
<!-- END:EVAL_RESULTS -->

- packaging validation: `openai`, `claude`, and `generic` targets pass contract checks
- packaging failure fixtures: invalid metadata, invalid YAML, and unsupported targets fail as expected
- failure library regressions: anti-pattern families pass automated checks

## What It Does

This project helps you create, refactor, evaluate, and package skills as durable capability bundles rather than one-off prompts.

The design logic is simple:

1. Capture the real recurring job behind the user's request.
2. Set a clean skill boundary so one package does one coherent job.
3. Optimize the trigger description before over-writing the body.
4. Keep the main skill file small and move details into references or scripts.
5. Add quality gates only when they pay for themselves.
6. Export compatibility artifacts only for the clients you actually need.

## Why It Exists

Most teams keep valuable operating knowledge scattered across chats, personal prompts, oral habits, and undocumented workflows. This project converts that hidden process knowledge into:

- discoverable skill packages
- repeatable execution flows
- lower-context instructions
- reusable team assets
- compatibility-ready distributions

## Repository Structure

```text
yao-meta-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── .gitignore
├── agents/
│   └── interface.yaml
├── evals/
├── examples/
├── references/
├── scripts/
└── templates/
```

## Core Components

### `SKILL.md`

The main skill entrypoint. It defines the trigger surface, operating modes, compact workflow, and output contract.

### `agents/interface.yaml`

The neutral metadata source of truth. It stores display and compatibility metadata without locking the source tree to one vendor-specific path.

### `references/`

Long-form material that should not bloat the main skill file. This includes design rules, evaluation guidance, compatibility strategy, and quality rubrics.

### `scripts/`

Utility scripts that make the meta-skill operational:

- `trigger_eval.py`: evaluates trigger descriptions with semantic intent concepts, explicit exclusions, and near-neighbor prompts
- `run_eval_suite.py`: runs train/dev/holdout trigger suites, reports family-level regressions, and fails if aggregate regressions appear
- `context_sizer.py`: estimates context weight and warns when the initial load gets too large
- `cross_packager.py`: builds client-specific export artifacts with explicit platform contracts and validation
- `init_skill.py`, `lint_skill.py`, `validate_skill.py`, `diff_eval.py`: minimal authoring toolchain

### `evals/`

Reusable trigger and packaging checks, including baseline and improved descriptions for comparison.

### `examples/`

End-to-end examples showing raw workflow input, design summary, and final generated skill shape, including one thicker complex benchmark and one evolution chain.

### `.github/workflows/test.yml`

Continuous integration entrypoint that runs the full local regression suite on push and pull request.

## Validation Notes

- Trigger evaluation now uses a local semantic-intent model with explicit positive concepts, exclusion concepts, and boundary-case reporting.
- The sample trigger report now covers a larger positive, negative, and near-neighbor set rather than a tiny demo set.
- Train/dev/holdout trigger suites now separate iterative tuning from final verification.
- Packaging validation now uses explicit contracts and YAML parsing, but it is still a lightweight local validation layer rather than a full platform integration suite.
- `evals/failure-cases.md` captures known weak spots that should remain part of regression checks.
- `failures/` captures reusable anti-pattern writeups and machine-runnable failure cases for routing, packaging, and authoring failures.
- `tests/verify_packager_failures.py` checks that invalid metadata, invalid YAML, and unsupported targets fail clearly.

### `templates/`

Starter templates for simple and more advanced skill packages.

## How To Use

### 1. Use the skill directly

Invoke `yao-meta-skill` when you want to:

- create a new skill
- improve an existing skill
- add evals to a skill
- convert a workflow into a reusable package
- prepare a skill for wider team adoption

### 2. Generate a new skill package

The typical flow is:

1. describe the workflow or capability
2. identify trigger phrases and outputs
3. choose scaffold, production, or library mode
4. generate the package
5. run the sizing and trigger checks if needed
6. export target-specific compatibility artifacts

### 3. Export compatibility artifacts

Examples:

```bash
python3 scripts/cross_packager.py ./yao-meta-skill --platform openai --platform claude --expectations evals/packaging_expectations.json --zip
python3 scripts/context_sizer.py ./yao-meta-skill
python3 scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json --baseline-description-file evals/baseline_description.txt
```

## Advantages

- **Neutral by default**: source files stay vendor-neutral, while adapters are generated only when needed.
- **Context efficient**: the project explicitly pushes detail out of the main skill file.
- **Evaluation-aware**: trigger and sizing checks are built into the workflow.
- **Reusable**: the output is a package, not just a paragraph of prompt text.
- **Portable**: compatibility is handled through packaging rather than duplicating source files for every client.

## Best Fit

This project is best for:

- agent builders
- internal tooling teams
- prompt engineers moving toward structured skills
- organizations building reusable skill libraries

## Documentation

| Language | Entry |
| --- | --- |
| English | [README.md](README.md) |
| 中文 | [docs/README.zh-CN.md](docs/README.zh-CN.md) |
| 日本語 | [docs/README.ja-JP.md](docs/README.ja-JP.md) |
| Français | [docs/README.fr-FR.md](docs/README.fr-FR.md) |
| Русский | [docs/README.ru-RU.md](docs/README.ru-RU.md) |

## Examples And Evals

- Examples: [examples/README.md](examples/README.md)
- Evals: [evals/README.md](evals/README.md)
- Failure library: [failures/README.md](failures/README.md)
- Failure regression check: [verify_failure_regressions.py](tests/verify_failure_regressions.py)
- Packaging contracts: [references/packaging-contracts.md](references/packaging-contracts.md)
- Platform capability matrix: [references/platform-capability-matrix.md](references/platform-capability-matrix.md)
- Failure fixtures: [tests/fixtures](tests/fixtures)
- Adapter snapshots: [tests/snapshots](tests/snapshots)
- Evolution example: [examples/evolution-frontend-review/README.md](examples/evolution-frontend-review/README.md)

## License

MIT. See [LICENSE](LICENSE).
