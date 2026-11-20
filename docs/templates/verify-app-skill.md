---
name: verify-<app>
description: Use only when the user explicitly invokes `$verify-<app>`. Run <app> the way a user would and collect evidence (screenshot/log/trace) that a change works. Return exactly one verdict: PASS, FAIL, or BLOCKED.
---

<!-- TEMPLATE: replace every placeholder with real commands and selectors from
the consumer repository, then delete this comment block. Another agent will
read this skill cold mid-session; it has never seen the app. Do not leave
placeholders. -->

# Verify <app>

## Required inputs

1. Commit SHA and branch (prefer an isolated worktree).
2. Feature Map file: `docs/feature-map/<feature>.md`.
3. Expected behavior and acceptance criteria (written before running).

## Procedure

1. Read the Feature Map and the real code **before** stating hypotheses.
2. **Launch**: `<exact command>`; ready when `<usable log line / prompt /
   health check>`; must start from an empty data directory (migrate + seed).
   Teardown: `<…>`.
3. **Doctor** (read-only; run first when anything looks wrong): `<process
   alive, correct version/build, owned port, auth still valid>`.
4. **Drive**: use the surface recipe; selectors from the Feature Map
   (ARIA/testid/prompt/route), never coordinates.
5. Bug fix: **reproduce on the baseline first**, keep the failing artifact;
   after the fix, rerun the *same* scenario on the *same* surface.
6. **Evidence** → `.artifacts/<run-id>/`: actions + resulting state (not only
   the final screen), console/server logs, side effects checked read-only.
7. **Cleanup**: stop only what this run started (never kill by process name);
   delete scratch; **keep artifacts**.

## Verdict (exactly one of three)

- `PASS`: scenario completed, every expectation met, no unexpected console/log
  errors outside the allow-list.
- `FAIL`: scenario ran but the result is wrong.
- `BLOCKED`: cannot conclude (missing fixture/tool, broken environment, stale
  selector). **Never return PASS.**
- Forbidden: rewriting acceptance criteria, fixtures, or selectors to force
  PASS. Forbidden: concluding "green build means it works."
- Stop after two unreproducible attempts and report the exact missing facts.

## Evidence standards

- Real user path; no internal setters or test-only endpoints.
- Mock only at production boundaries that already isolate external systems.
- Dry-run: verify by observation what was actually skipped.

## Helpers

- `<script>`: how to invoke `<…>` (script must be executable and show a
  call example in this file).

## Report

Return: verdict, commands run, artifact paths, Feature Map used, and what
this run did not prove (for example environment differences).
