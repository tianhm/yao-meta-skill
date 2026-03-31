---
name: release-orchestrator
description: Coordinate software release preparation, rollout readiness, migration notes, rollback planning, and stakeholder communication. Use when asked to prepare a release, build a rollout checklist, review release risk, or organize launch readiness.
---

# Release Orchestrator

## Workflow

1. Gather release inputs: changes, risks, migrations, dependencies.
2. Build artifacts for changelog, rollout, rollback, and announcements.
3. Flag missing release-critical information before declaring readiness.
4. Output a release package with clear go/no-go signals.

## Reference Map

- Read `references/release-checklist.md` for the stage checklist.
- Use `scripts/build_release_packet.py` for deterministic artifact assembly.
