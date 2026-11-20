---
name: guardrails
description: Use only when the user explicitly invokes `$guardrails`. Bootstrap deterministic architecture gates, lint starters, a verification skill, and an evolution loop for a consumer repository. References and templates structure the work; the consumer owns all policy and tooling.
---

# Guardrails

Help a consumer repository build deterministic guards so agents are forced to
write correct code by default. Follow the inverted-pyramid investment order:
codebase and architecture first, static analysis and tests second, runtime
verification third, prose rules last and thinnest.

This skill is a structured bootstrap, not a mandate. The consumer owns their
architecture, lint tooling, verification, and policy. References provide
starting points; templates provide structure. Use `$encode-invariant` for the
authority-gated encoding flow and `$improve-harness` for measured skill
revisions.

## Safety Contract

- Read applicable `AGENTS.md` and `docs/WORKFLOW.md` before inspecting.
- The first pass is always inspection and proposal. Do not install lint
  configs, hooks, CI changes, or verification tooling without explicit user
  approval.
- Do not infer consumer policy from conventions, code patterns, tests,
  defaults, or undocumented preferences.
- Templates are optional structure, not authority. Leave a template section
  empty rather than fabricating content.
- `check_architecture.py` is a reference tool. Prefer the consumer's native
  AST/compiler tools (ESLint, ruff, Roslyn, clippy, depguard) for precision.

## Workflow

### 1. Assess the current state

Inspect the consumer repository's architecture, lint setup, test coverage,
and any existing verification or feature maps. Use `$onboard-repository`
if the repository is unfamiliar.

Produce a rule-table draft using `docs/templates/rule-table.md`:

| Rule | Pyramid tier | Enforcement mechanism | Evidence | Baseline |
| --- | --- | --- | --- | --- |

Classify each rule's enforcement: T1 (architecture/design), T2
(lint/type/test), T3 (runtime verification), T4 (prose only). Rules
without enforcement are prose; they must genuinely require judgment.

### 2. Bootstrap architecture gates

Read [references/architecture-lint.md](references/architecture-lint.md) for
the rule catalog, error-message formula, per-stack tool matrix, and baseline
ratchet strategy.

For the consumer's stack, propose the smallest set of deterministic guards
using native tools. Use `check_architecture.py` as a stack-agnostic fallback
when no native tool covers the boundary. Every guard must have an actionable
error message following the formula: WHAT (violation) — WHY (one sentence) —
FIX (concrete compliant action with real paths).

Apply the baseline ratchet on legacy codebases: freeze existing violations,
fail only on new ones, sweep old violations in small batches.

### 3. Set up verification

Read [references/verification-design.md](references/verification-design.md).

Propose a `verify-<app>` skill using `docs/templates/verify-app-skill.md`.
Seed a Feature Map using `docs/templates/feature-map-index.md` and
`docs/templates/feature-map-entry.md`. The Feature Map must use stable
selectors (ARIA roles, test IDs, route paths), not coordinates or generated
class names.

The verification skill must produce a verdict: PASS (all expectations met),
FAIL (expectations violated), or BLOCKED (cannot conclude). BLOCKED must
never be promoted to PASS. Weakening criteria to achieve PASS is prohibited.

### 4. Propose the evolution loop

Read [references/evolution-loop.md](references/evolution-loop.md).

Propose the evolution-loop checklist from
`docs/templates/pr-verification-checklist.md` for the consumer's PR workflow.
Each recurring agent mistake should escalate through the pyramid: observe,
classify to the highest feasible tier, clean up old violations, measure, and
retire the manual review item.

### 5. Set up skill evaluation (optional)

Read [references/verification-design.md](references/verification-design.md)
section on skill evaluation.

Use `docs/templates/skill-eval-rubric.md` to propose an eval structure.
Evals use a blind judge (different model family from the worker), neutral
directory names, and organic prompts. Use `$improve-harness` for measured
skill revisions driven by eval results.

### 6. Report

Return:

- rule table with enforcement classification;
- proposed guards and their error messages;
- verification skill proposal and Feature Map seed;
- evolution-loop checklist;
- what remains unguarded and why;
- baseline counts if ratcheting.

## References

- [references/inverted-pyramid.md](references/inverted-pyramid.md):
  investment-order principles.
- [references/architecture-lint.md](references/architecture-lint.md): rule
  catalog, error-message formula, tool matrix, ratchet strategy, lint
  starters.
- [references/verification-design.md](references/verification-design.md):
  runtime verification, Feature Map, eval design.
- [references/evolution-loop.md](references/evolution-loop.md): five-step
  escalation checklist.
- [tools/check_architecture.py](tools/check_architecture.py): stack-agnostic
  architecture gate.
