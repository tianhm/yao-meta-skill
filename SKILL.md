---
name: yao-meta-skill
description: Create, refactor, evaluate, and package agent skills from workflows, transcripts, prompts, docs, or rough notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, optimize skill triggering, add evals, or prepare a skill for team reuse. Relevant for meta-skills, skill factories, skill templates, skill QA, and cross-platform skill packaging.
metadata:
  author: Yao Team
  philosophy: "structured design, evaluation loop, template ergonomics, operational packaging"
---

# Yao Meta Skill

Build skills as reusable products, not long prompts.

## Core Rules

- Treat a skill as a maintained capability package.
- Write the frontmatter `description` early; it is the main trigger surface.
- Keep `SKILL.md` lean. Put detail in `references/`, deterministic logic in `scripts/`, and output artifacts in `assets/`.
- Use the lightest process that still protects quality.
- Package for reuse only when the user actually needs reuse.

## Use Cases

Use this skill to:

- create a new skill
- turn a workflow, runbook, transcript, or prompt set into a skill
- improve a skill's boundary, description, evals, or packaging
- design a team skill template or skill-library standard
- migrate a skill toward the Agent Skills open format

## Modes

Choose the lightest mode that fits.

### Scaffold

Use for exploratory or personal skills.

Deliver:

- `SKILL.md`
- `agents/interface.yaml`
- `references/` only if clearly needed

### Production

Use for reusable team skills.

Deliver:

- concise package structure
- focused `references/`
- `scripts/` when prose would be brittle or repetitive
- `evals/` when output quality can be checked

### Library

Use for important organizational skills or meta-skills.

Add:

- trigger positives, negatives, and near neighbors
- revision rubric
- packaging guidance
- maintenance metadata when useful

## Factory Components

Use these when they materially improve quality:

- `templates/basic_skill.md.j2`
- `templates/complex_skill.md.j2`
- `scripts/trigger_eval.py`
- `scripts/context_sizer.py`
- `scripts/cross_packager.py`

## Workflow

### 1. Capture the real job

Infer:

- the recurring task or decision
- likely trigger phrases and contexts
- expected outputs
- what must be deterministic
- whether the skill is personal, team, or cross-platform

Keep discovery lean. Default to no more than two clarification rounds unless guessing is risky.

### 2. Set the boundary

One skill should usually have:

- one capability family
- one trigger surface
- one coherent workflow

Split oversized skills. Move variants into `references/` or sibling skills.

### 3. Design the trigger

The `description` should say:

- what the skill does
- when to use it
- phrases, artifacts, or file types that should trigger it
- adjacent cases that are easy to miss

For important skills, create `should_trigger`, `should_not_trigger`, and near-neighbor prompts. Use `scripts/trigger_eval.py` when helpful.

### 4. Write the package

Default structure:

```text
skill-name/
├── SKILL.md
├── agents/interface.yaml
├── references/
├── scripts/
├── assets/
└── evals/
```

Only create folders that earn their keep. Start from the basic template unless the skill clearly needs the complex one.

### 5. Add quality gates

Use the minimum useful QA:

- basic: structure and naming check
- standard: realistic prompts and expected outcomes
- advanced: trigger evals, benchmark comparisons, revision loop

For production or library-grade skills, run `scripts/context_sizer.py` before finalizing.

### 6. Package for reuse

If team reuse matters, include:

- stable folder name
- aligned `agents/interface.yaml`
- minimal tool assumptions
- version or maintenance metadata when useful
- target-specific packaging only for requested platforms

Use `scripts/cross_packager.py` when packaging artifacts are needed.

### 7. Report the result

Summarize:

- what was packaged
- what trigger surface was chosen
- what was excluded
- what quality gates exist
- what should be improved next

## Output Contract

Unless the user asks otherwise, produce:

1. a working skill directory
2. a trigger-aware `SKILL.md`
3. aligned `agents/interface.yaml`
4. references only where they reduce context bloat
5. optional scripts, evals, and `manifest.json` when justified

## Reference Map

- [Skill Design Guidelines](references/skill_design_guidelines.md)
- [Client Compatibility](references/client-compatibility.md)
- [Comparative Analysis](references/comparative-analysis.md)
- [Meta-Skill Rubric](references/design-rubric.md)
- [Skill Template](references/skill-template.md)
- [Trigger And Eval Playbook](references/eval-playbook.md)
