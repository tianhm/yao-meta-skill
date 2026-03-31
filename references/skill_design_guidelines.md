# Skill Design Guidelines

This document captures the operating rules for `yao-meta-skill`.

## 1. Treat Skill Creation As Product Design

A generated skill should answer these questions clearly:

- What exact recurring job does this package improve?
- Who is the intended user or agent?
- What is in scope and out of scope?
- What should be stable across runs?
- What is expected to evolve over time?

## 2. Separate Three Kinds Of Content

Put each kind of content in the right place:

- `SKILL.md`: core workflow, trigger surface, decision rules
- `references/`: detailed domain material, examples, schemas, policy docs
- `scripts/`: deterministic or brittle operations

If you mix all three into `SKILL.md`, quality and maintainability drop fast.

## 3. Use A Trigger Matrix

Every important skill should have a trigger matrix:

- positive prompts
- clear negatives
- near neighbors

The goal is not just "can it trigger", but "does it trigger at the right boundary".

## 4. Keep The Body Small On Purpose

Do not optimize only for completeness.

Optimize for:

- low context cost
- clear branch selection
- discoverable references
- safe defaults

## 5. Add Lifecycle Metadata Only When It Helps

For personal or disposable skills, extra metadata can be noise.

For shared skills, a `manifest.json` is useful for:

- owner
- version
- updated_at
- target platforms
- review cadence

## 6. Prefer Progressive Industrialization

Move through these stages:

1. Working draft
2. Trigger-hardened draft
3. Reusable team skill
4. Governed skill asset

Do not start every skill at stage 4.
