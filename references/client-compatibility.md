# Client Compatibility

This skill package uses a neutral source-of-truth file:

- `agents/interface.yaml`

That file is the canonical metadata source for display name, short description, default prompt, and adapter targets.

## Compatibility Strategy

Use a two-layer model:

1. **Canonical source**
   - Keep brand-neutral metadata in `agents/interface.yaml`.
   - Keep behavior in `SKILL.md`, `references/`, and `scripts/`.

2. **Adapter outputs**
   - Generate client-specific metadata only when exporting or packaging.
   - Do not keep vendor-specific metadata files in the source tree unless a client strictly requires them.

## Supported Targets

The current adapter flow is designed for:

- OpenAI-compatible clients
- Claude-compatible clients
- generic Agent Skills clients

## Compatibility Rules

- Keep `SKILL.md` as the primary behavior definition.
- Keep client metadata minimal and presentation-focused.
- Avoid putting client-specific logic in the main workflow.
- Prefer packaging-time conversion over source-tree duplication.
