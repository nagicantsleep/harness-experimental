# 0029 Guardrails Opt-In Payload

Date: 2026-11-20

## Status

Accepted.

## Context

Decision 0020 established one core profile plus independent opt-in add-ons.
Decision 0028 provided one authority-gated invariant-encoding flow. These do
not supply a structured path from a diagnosed agent mistake to a deterministic
guard, baseline ratchet, running-app verification, or skill evaluation.

Lauren Tan's published methodology (talk "All Code Is Slop (Except Mine)",
AI Engineer CODE 2026; workshop Vision Sabbat 2026-09; pstack plugin
`cursor/plugins/tree/main/pstack`) demonstrates an inverted-pyramid investment
order: codebase/architecture, then static analysis/tests, then runtime
verification, then prose rules as the thinnest layer. Key verified principles
include: lint diagnostics that teach the fix, baseline ratchets for legacy
repos, feature maps from the user perspective, agents self-verifying on a
running app, skill evals with a blind judge, and an evolution loop that
escalates recurring agent mistakes into deterministic guards.

A standalone prototype (`poteto-harness`) was built and tested against these
sources. This decision ports the verified, stack-agnostic subset into the
repository harness as a second independent opt-in add-on, following the same
pattern as engineering wisdom.

## Decision

1. `--with-guardrails` installs an explicit-only skill with reference
   material and templates declared in `scripts/guardrails-install-files.txt`.
   It follows the engineering-wisdom precedent: no hidden state, no consumer
   policy, no implicit activation.
2. The guardrails skill provides:
   - reference material on the inverted-pyramid investment order, architecture
     and lint design, runtime verification, and the evolution loop;
   - `check_architecture.py`: a stack-agnostic architecture gate with layer
     checks, banned-pattern detection, comment/suppression auditing, and a
     baseline ratchet (only new violations fail; error messages explain the
     fix);
   - per-stack lint starter reference covering TypeScript, Python, .NET,
     Go/Rust, and Godot;
   - a `verify-app` skill template and Feature Map template so agents prove
     changes on the running app;
   - a skill-eval rubric template with blind-judge and neutral-environment
     guidance;
   - a PR verification checklist template;
   - an evolution-loop checklist for escalating agent mistakes; and
   - a rule-table template mapping rules to their enforcement mechanism.
3. The tool (`check_architecture.py`) is Python, consistent with decision 0026
   allowing Python for explicitly-invoked skills. It is a reference
   implementation, not a mandatory consumer dependency. Consumer architectures
   should prefer their native AST/compiler tools for precision; the script
   serves as a stack-agnostic fallback.
4. Per-stack lint configs are reference material within the skill, not
   installed consumer files. The consumer owns their lint toolchain.
5. Integration with existing skills is through reference, not duplication:
   - `$onboard-repository` already compares invariants with checks; a guardrails
     consumer can use its Feature Map template during onboarding.
   - `$encode-invariant` provides the authority-gated encoding flow; guardrails
     references name it as the path from rule-table entry to mechanical guard.
   - `$improve-harness` provides the measured-improvement loop; guardrails
     references name it as the path for skill-eval-driven revisions.
6. Content tagged `[ADDED]` in the prototype (PASS/FAIL/BLOCKED verdicts,
   holdout cases, numeric exit gates, phased-rollout milestones) is included
   as advisory material clearly labeled, not as repository authority.
7. Items left out of this payload:
   - `scout.py` and `evolve_loop.py` are experimental `[ADDED]` tools; they
     can follow as a future opt-in if demand arises.
   - Playbook router and individual playbooks; the repo has no playbook
     concept and adding one would create a new workflow engine.
   - CI template; the consumer owns CI configuration.
   - Per-stack lint config files as installed payload; the consumer owns their
     lint setup and the reference documents explain how to set it up.

## Alternatives Considered

1. **Merge into core.** Rejected because decision 0020 keeps the core small
   and free of opinionated methodology.
2. **Create a separate repository.** Rejected because the updater and release
   train already support opt-in manifests.
3. **Port `check_architecture.py` to Rust.** Considered but deferred. The
   tool is a reference implementation consumers may replace with native AST
   tools. Python matches the existing skill-script precedent (decision 0026)
   and enables direct consumer customization without a Rust toolchain.
4. **Install per-stack lint configs into the consumer.** Rejected because the
   consumer owns their lint toolchain and installed configs would falsely
   appear authoritative.
5. **Include `scout.py` and `evolve_loop.py`.** Deferred because they are
   `[ADDED]` experimental tools not verified against primary sources.

## Consequences

Positive:

- Consumers who opt in receive a structured path from agent mistakes to
  deterministic guards.
- The baseline ratchet allows gradual adoption on legacy codebases.
- Verification and eval templates close the loop between agent changes and
  observable proof.
- Existing skills remain composable without duplication.

Tradeoffs:

- The managed payload grows by one skill and its references and templates.
- `check_architecture.py` is regex-based and approximate; consumers must
  verify false-positive rates and prefer native AST tools where possible.
- Python is required only when the guardrails skill is explicitly invoked;
  ordinary work does not need it.
- Consumer edits to managed guardrails files can produce three-way update
  conflicts.

## Follow-Up

- Exercise the payload on a consumer repository and measure false-positive
  rates for the architecture gate.
- Evaluate whether `scout.py` and `evolve_loop.py` warrant a future opt-in.
- Track demand for Rust-native architecture checking.
