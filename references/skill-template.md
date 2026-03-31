# Skill Template

Use this skeleton when generating a new skill.

```markdown
---
name: skill-name
description: Describe what the skill does and when to use it. Include realistic trigger phrases, task types, artifacts, or adjacent scenarios that should activate it.
metadata:
  author: Your team
---

# Skill Title

One-sentence summary of the capability.

## When To Use This Skill

- Trigger scenario 1
- Trigger scenario 2
- Trigger scenario 3

## Workflow

### 1. Understand the request

- Identify the actual job to be done
- Check assumptions and inputs

### 2. Choose the path

- Use path A when ...
- Use path B when ...

### 3. Execute

- Step 1
- Step 2
- Step 3

### 4. Validate

- Minimum acceptance checks

## Reference Map

- Read `[topic-a](references/topic-a.md)` when ...
- Read `[topic-b](references/topic-b.md)` when ...
```

## Optional Folders

Create only when justified:

- `agents/interface.yaml`
- `references/`
- `scripts/`
- `assets/`
- `evals/`

## agents/interface.yaml Template

```yaml
interface:
  display_name: "Human Friendly Name"
  short_description: "Short capability summary"
  default_prompt: "Use $skill-name to ..."
compatibility:
  canonical_format: "agent-skills"
  adapter_targets:
    - "openai"
    - "claude"
    - "generic"
```
