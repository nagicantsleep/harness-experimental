# Skill Eval Rubric — <skill name>

Eval = unit test for a skill. For the judge only. Workers must not see this
file. Directory and prompt names the worker sees must avoid: `eval`, `test`,
`judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`,
`arena`.

## Variant under test

- Skill / playbook:
- Behavioral success looks like:

## Rubric (3–6 criteria)

| # | Criterion (observable) | Pass | Fail |
| --- | --- | --- | --- |
| 1 | | | |
| 2 | | | |
| 3 | | | |

## Setup

- Neutral worker directories:
- Organic user prompt (goal only; no measurement hints):
- Models / worker count:
- Judge model (different family from workers):

## Fixtures `[ADDED]`

| Group | Case | Expected verdict / behavior |
| --- | --- | --- |
| broken | | FAIL with evidence |
| working | | PASS with evidence |
| missing-prereq | | BLOCKED (honest; no fabricated PASS) |
| holdout (hidden from author) | | |

## Results

| Worker | Model (hidden from judge) | Score | Notes from real transcript |
| --- | --- | --- | --- |
| | | | |

## Decision

- Promote / revise / remove:
- Budget used (rounds, tokens):
- Remaining risks:
