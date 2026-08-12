---
name: yao-meta-skill
description: Create, improve, or evaluate an existing skill from workflows, prompts, SOPs, scripts. Use for migration/release/package, routing, evals/tests, install/trust checks, 优化已有 skill, 补 trigger 评测. Exclude summary/translation/docs, brainstorming, one-off prompts, copy-only edits, outline-only requests.
metadata:
  author: Yao Team
---

# Yao Meta Skill

## Router Rules

- Route by frontmatter `description`; use the lightest reliable process.
- Keep `SKILL.md` lean; route guidance to `references/`, logic to `scripts/`, evidence to `reports/`.

## Modes

- `Scaffold`: exploratory. `Production`: team reuse. `Library`: shared infra. `Governed`: release-critical.
- Rules: [Method](references/skill-engineering-method.md), [Modes](references/operating-modes.md), [Boundaries](references/resource-boundaries.md).

## Compact Workflow

1. One-off/no reusable process: `Do not create a skill`; `near-neighbor`; require `repeated use` + `reusable output contract`.
2. Capture job, output, exclusions, constraints, standards, lightest fit.
3. Scan `3-5` external/user/local references when useful.
4. Write `description` early; route edits need `trigger_eval.py`; releases need risk-matched gates.
5. Add deeper profiles and iteration directions only when earned.

Playbooks: [Method](references/skill-engineering-method.md), [Intent](references/intent-dialogue.md), [Skill IR](references/skill-ir-method.md), [Output Eval](references/output-eval-method.md), [Review Studio](references/review-studio-method.md).

## Skill OS 2.0 Gates

For production/library/governed releases, run Skill IR, compiler, trigger/output eval, Skill Atlas, conformance, trust, registry/package/install, upgrade, drift, waiver, Review Studio.

## Governed Package Boundary

For file-backed/governed packages, name `input_files` as `file-backed fixture`; include `owner`, `review cadence`, `input_files`, `output contract`, `rollback boundary`; require `trust report` and `reports/output_quality_scorecard.md`; mark unavailable telemetry/approvals/metrics/benchmarks as `missing evidence`; do not fabricate evidence.

Preserve labels literally when they apply: `file-backed fixture`, `input_files`, `output contract`, `rollback boundary`, `trust report`, `reports/output_quality_scorecard.md`, `missing evidence`.

## First-Turn Style

- Start from the user's work and outcome.
- Ask only `2-3` key questions unless enough detail exists.
- In Chinese, sound soft and companion-like; use [Intent Dialogue](references/intent-dialogue.md).

## Output Contract

Create/refactor/package: produce `SKILL.md`, aligned `agents/interface.yaml`, justified assets, and boundary/gate summary. Audit/evaluate-only: findings + proposed fixes; edit only when asked. No-skill: no files.

## Reference Map

Primary: [Method](references/skill-engineering-method.md), [Artifact Design](references/artifact-design-doctrine.md), [Systems](references/systems-thinking-doctrine.md), [Governance](references/governance.md), [SkillOps](references/skillops-decision-policy.md).
