# Meta-Skill Rubric

Score each generated skill from 1 to 5 on each dimension.

## 1. Trigger Clarity

Questions:

- Does the description say what the skill does?
- Does it say when to use it?
- Does it include realistic trigger phrases and adjacent cases?
- Is it likely to reduce under-triggering?

## 2. Boundary Clarity

Questions:

- Is the skill solving one coherent capability family?
- Are unrelated tasks excluded?
- Are variants separated cleanly into references or sibling skills?

## 3. Context Efficiency

Questions:

- Is `SKILL.md` lean?
- Are details pushed into `references/`?
- Are scripts used where prose would be brittle or repetitive?

## 4. Execution Reliability

Questions:

- Are the workflow steps actionable?
- Are critical constraints explicit?
- Are deterministic steps captured in scripts or templates?
- Is there a clear failure-handling path?

## 5. Evaluation Quality

Questions:

- Are there realistic usage prompts?
- Are there trigger positives and negatives for important skills?
- Is there a way to compare revisions?

## 6. Reuse And Maintenance

Questions:

- Can another teammate discover and reuse the skill?
- Is `agents/interface.yaml` aligned with the package?
- Are ownership and future iteration obvious?

## 7. Portability

Questions:

- Does the package stay close to the open format?
- Are tool-specific assumptions minimized or isolated?
- Can the skill be adapted to another compatible client without rewrite?

## Interpretation

- `30+`: production-ready
- `24-29`: solid but improve weak dimensions
- `18-23`: usable draft, not yet robust
- `<18`: redesign the boundary or trigger strategy
