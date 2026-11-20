# Installation Contract

Harness has one product profile and two independent opt-in add-ons.

## Core

The exact core payload is declared in
`scripts/harness-install-files.txt`. It contains generic repository guidance,
optional knowledge and planning references, and explicit-only discovery,
audit, invariant-encoding, and improvement skills. Installation does not
activate skills or impose a task workflow.

The platform bootstrap installs a checksum-verified `harness` binary under
`scripts/bin/` and delegates installation or update to that candidate.

Core installation:

- records exact upstream bytes under `.harness-core/`;
- preserves consumer files through merge or human-directed conflict handling;
- backs up replaced files;
- does not install an application stack or product policy;
- does not install schemas, databases, orchestration, or background processes;
- does not delete pre-existing legacy Harness files.

## Engineering Wisdom Add-On

`--with-engineering-wisdom` or `-WithEngineeringWisdom` copies the
explicit-only advisory skill declared in
`scripts/engineering-wisdom-install-files.txt`.

Omitting the flag does not install or activate the skill. A later install
without the flag leaves an existing copy untouched. Removal is explicit and
stateless: delete only `.agents/skills/engineering-wisdom/`.

Advice cannot establish consumer policy or authorize an architecture rewrite.

## Guardrails Add-On

`--with-guardrails` or `-WithGuardrails` copies the explicit-only
guardrails skill declared in `scripts/guardrails-install-files.txt`.

The add-on includes reference material on the inverted-pyramid investment
order, a stack-agnostic architecture gate with baseline ratchet, verification
and Feature Map templates, skill-eval and evolution-loop checklists, and a PR
verification checklist. It does not install per-stack lint configs into the
consumer, does not activate skills, and does not establish consumer policy.

Omitting the flag does not install or activate the skill. A later install
without the flag leaves an existing copy untouched. Removal is explicit and
stateless: delete only `.agents/skills/guardrails/` and the guardrails-owned
templates listed in the manifest.

`check_architecture.py` is a reference tool. Prefer the consumer's native
AST/compiler tools for precision. Python is required only when the skill is
explicitly invoked.

See decision 0029 for the design rationale and what was left out.

## Merge And Override

- `--merge` / `-Merge`: preserve existing files and add missing managed
  paths.
- `--override` / `-Override`: back up and replace protected Harness paths.
- `--force` / `-Force`: overwrite individual managed files with backups.
- `--dry-run` / `-DryRun`: preview without writing.

## Update

`harness update` verifies release identity and checksum, compares installed
base, local bytes, and incoming bytes, and applies the complete plan
transactionally.

Overlapping text edits stage a frozen resolution session. Structural conflicts
must be corrected before replanning. Successful activation writes provenance
last and replaces only the selected repository's executable after core files
succeed.

## Removed Profile

The former `--with-cli`, `--upgrade-cli`, `-WithCli`, and `-UpgradeCli`
profiles ended with protocol v1. Current installers reject those options.
Existing consumer databases and binaries are not automatically deleted.
