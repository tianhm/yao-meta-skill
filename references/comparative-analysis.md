# Comparative Analysis

This reference distills four meta-skill archetypes into one design system.

## Shared Logic

All four approaches converge on the same model:

1. A skill is a folderized capability package, not a prompt snippet.
2. Frontmatter description is the trigger surface.
3. Long instructions should be split by progressive disclosure.
4. Skills are most valuable for repeated, multi-step, tool-using workflows.
5. Skills become more valuable when they are portable, maintainable, and shareable.

## Structure-First Creator

Primary strengths:

- clear structure and boundary discipline
- strong context-efficiency mindset
- good guidance on progressive disclosure
- pragmatic skeleton for authoring without overbuilding

Primary gaps:

- lighter on trigger benchmarking than the eval-first archetype
- lighter on distribution and registry than the factory archetype
- less opinionated on organizational operations beyond good authoring practice

Use it for:

- canonical package structure
- concise writing standard
- deciding what belongs in `SKILL.md` vs `references/`

## Eval-First Creator

Primary strengths:

- eval-first mindset
- explicit trigger optimization
- positive and negative prompt testing
- iterative improvement loop with benchmark thinking

Primary gaps:

- heavier process cost
- more suitable for high-value skills than quick one-offs
- some workflow assumptions are tied to a specific runtime style

Use it for:

- trigger eval design
- benchmark loops
- systematic improvement of important skills

## Template-First Scaffold

Primary strengths:

- fast onboarding
- clean scaffold
- easy explanation of required fields
- good for normalizing team authoring habits

Primary gaps:

- shallow evaluation model
- limited operations guidance after scaffolding
- more a template than a full skill engineering system

Use it for:

- starter layout
- contributor onboarding
- low-friction authoring workflow

## Factory-First Builder

Primary strengths:

- strongest productization instinct
- cross-platform packaging and export thinking
- validation, security, staleness, and registry mindset
- closest to a skill factory instead of a skill template

Primary gaps:

- heavier system and maintenance cost
- portability requires adaptation layers in practice
- may be excessive for small personal skills

Use it for:

- distribution and registry model
- packaging lifecycle
- maintenance and governance thinking

## Yao Synthesis

The right synthesis is:

- **structure-first for clarity**
- **eval-first for reliability**
- **template-first for onboarding**
- **factory-first for operations and scale**

That combination yields a meta-skill that is:

- lightweight enough to use often
- rigorous enough for important skills
- structured enough for team adoption
- operational enough for long-term reuse
