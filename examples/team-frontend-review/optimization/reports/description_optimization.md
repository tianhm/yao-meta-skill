# Frontend Review Description Optimization

Winner: `Current`

- current tokens: `50`
- winner tokens: `50`
- baseline tokens: `52`

## Winner

Review frontend code for accessibility, UI security, missing states, and UX regressions. Use when asked to review React components, run a pre-merge frontend review, or check a11y and unsafe rendering.

## Candidate Ranking

| Candidate | Tokens | Dev FP | Dev FN | Dev Near | Holdout FP | Holdout FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Current` | 50 | 0 | 3 | 1.0 | 0 | 0 |
| `Guardrail` | 62 | 0 | 3 | 1.0 | 0 | 0 |
| `Balanced` | 64 | 0 | 3 | 1.0 | 0 | 0 |
| `Artifact Aware` | 84 | 0 | 3 | 1.0 | 0 | 0 |
| `Boundary` | 90 | 0 | 3 | 1.0 | 0 | 0 |

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
