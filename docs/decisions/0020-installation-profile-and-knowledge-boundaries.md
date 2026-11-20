# 0020 Installation Profile And Knowledge Boundaries

Date: 2026-07-21

## Status

Accepted. Amended by decisions 0026 and 0027.

## Context

Decision 0019 made the repository-centered workflow authoritative. Installation
must make the repository ownership boundary physically true: a consumer should receive generic
repository guidance and the safe maintenance binary without upstream product
history, application assumptions, or a second source of truth.

Decision 0026 added explicit-only onboarding skills to the core. Decision 0027
ended the former compatibility profile rather than continuing a two-product
installer.

## Decision

Harness has one product profile: **core**.

Core installs:

- the compact repository map and capability/evidence context;
- optional product, plan, and decision locations;
- optional templates for durable plans, decisions, runbooks, and measured
  Harness improvements;
- explicit-only onboarding and proposal-audit skills; and
- the checksum-verified Rust `harness` maintenance binary.

Core does not install:

- consumer product policy or architecture;
- application commands, credentials, fixtures, logs, or validation;
- a database, schemas, orchestration, or background processes; or
- upstream history, tests, CI, release scripts, and product decisions.

The engineering-wisdom advisory skill and the guardrails skill are independent
explicit opt-ins, not second product profiles. They store no state and
establish no consumer policy. See decisions 0026 and 0029.

Installation and updates preserve unknown existing files. In particular, they
do not automatically delete artifacts from the end-of-life compatibility
product. Removal of consumer-owned legacy bytes requires a separate explicit
decision in that repository.

## Alternatives Considered

1. **Keep a compatibility profile.** Superseded by decision 0027 because its
   implementation and release train kept two products in one repository.
2. **Install upstream architecture and examples.** Rejected because their names
   and placement would make them appear authoritative for the consumer.
3. **Offer many feature flags.** Rejected because combinatorial profiles obscure
   the small stable core.
4. **Install advisory philosophy by default.** Rejected because repository
   authority, not upstream taste, must decide engineering policy.

## Consequences

- Fresh installations have one product and one authority path.
- Consumer repositories receive no fabricated application truth.
- The installed binary can safely deliver later core improvements.
- Historical product implementations remain in Git rather than in consumer
  payloads or current documentation search.
