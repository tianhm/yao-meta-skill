# Root Description Optimization

Winner: `Current`

- current tokens: `65`
- winner tokens: `65`
- baseline tokens: `8`

## Winner

Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, add evals, or package a skill for team reuse.

## Candidate Ranking

| Candidate | Tokens | Dev FP | Dev FN | Dev Near | Holdout FP | Holdout FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Current` | 65 | 0 | 0 | 1.0 | 0 | 0 |
| `Minimal` | 41 | 2 | 1 | 0.857 | 0 | 0 |
| `Balanced` | 54 | 2 | 1 | 0.857 | 0 | 0 |
| `Artifact Aware` | 72 | 2 | 1 | 0.857 | 0 | 0 |
| `Boundary` | 78 | 2 | 1 | 0.857 | 0 | 0 |
| `Guardrail` | 50 | 5 | 1 | 0.429 | 2 | 0 |

## Acceptance Gates

| Gate | Winner FP | Winner FN | Current FP | Current FN | Baseline FP | Baseline FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Holdout | 0 | 0 | 0 | 0 | 0 | 0 |
| Blind Holdout | 0 | 0 | 0 | 0 | 0 | 0 |

## Selection Logic

Ordered by:
- fewest false positives
- fewest false negatives
- highest near-neighbor pass rate
- highest negative pass rate
- highest precision
- highest recall
- shortest description
