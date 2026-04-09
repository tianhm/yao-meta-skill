---
name: yao-meta-skill
description: Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, add evals, or package a skill for team reuse.
metadata:
  author: Yao Team
  philosophy: "structured design, evaluation loop, template ergonomics, operational packaging"
---

# Yao Meta Skill

Build reusable skill packages, not long prompts.

## Router Rules

- Route by frontmatter `description` first.
- Keep `SKILL.md` to routing plus a minimal execution skeleton.
- Put long guidance in `references/`, deterministic logic in `scripts/`, and evidence in `reports/`.
- Use the lightest process that still makes the skill reliable.

## Modes

- `Scaffold`: exploratory or personal use.
- `Production`: team reuse with focused gates.
- `Library`: shared infrastructure or meta skill.

Mode rules: [Operating Modes](references/operating-modes.md), [QA Ladder](references/qa-ladder.md), [Resource Boundary Spec](references/resource-boundaries.md), [Skill Engineering Method](references/skill-engineering-method.md).

## Compact Workflow

1. Decide whether the request should become a skill, then choose the lightest archetype.
2. Run a short intent dialogue to capture the recurring job, outputs, trigger phrases, exclusions, and constraints.
3. Run a short reference scan with external benchmark objects first; use local files only for fit, privacy, and compatibility calibration.
4. Write the `description` early, then test route quality before expanding the package.
5. Add only the folders and gates that earn their keep: `trigger_eval.py`, `optimize_description.py`, `judge_blind_eval.py`, `resource_boundary_check.py`, `governance_check.py`, `cross_packager.py`.
6. After the first package exists, surface the top three next iteration directions instead of expanding the skill in every direction at once.

Core playbooks: [Method](references/skill-engineering-method.md), [Intent Dialogue](references/intent-dialogue.md), [Reference Scan](references/reference-scan.md), [Archetypes](references/skill-archetypes.md), [Gate Selection](references/gate-selection.md), [Iteration Philosophy](references/iteration-philosophy.md), [Non-Skill Decision Tree](references/non-skill-decision-tree.md), [Eval Playbook](references/eval-playbook.md).

## Output Contract

Unless the user asks otherwise, produce:

1. a working skill directory
2. a trigger-aware `SKILL.md`
3. aligned `agents/interface.yaml`
4. optional `references/`, `scripts/`, `evals/`, `reports/`, and `manifest.json` only when justified
5. a short summary of boundary, exclusions, benchmark objects, gates, and next steps

## Reference Map

Primary references: [Method](references/skill-engineering-method.md), [Reference Scan](references/reference-scan.md), [Intent Dialogue](references/intent-dialogue.md), [Archetypes](references/skill-archetypes.md), [Gate Selection](references/gate-selection.md), [Iteration Philosophy](references/iteration-philosophy.md), [Governance](references/governance.md), [Resource Boundaries](references/resource-boundaries.md), [Eval Playbook](references/eval-playbook.md).
