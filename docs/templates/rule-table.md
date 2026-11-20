# Rule Table

Map every accepted rule to its enforcement mechanism. A rule without
enforcement is prose and must genuinely require judgment.

| Rule | Pyramid tier (T1–T4) | Enforcement mechanism | Evidence of first encoding | Baseline count |
| --- | --- | --- | --- | --- |
| | | | | |

## Tier legend

- **T1**: Architecture / design change that makes the mistake inexpressible.
- **T2**: Static check (type, lint, dependency graph, behavior test).
- **T3**: Runtime verification (Feature Map journey, formal, PBT).
- **T4**: Prose (skill, playbook, AGENTS.md) — judgment only.

When a recurring agent mistake matches a rule that has no enforcement,
escalate the tier in the same change. Remove a rule when the class of error
can no longer occur.
