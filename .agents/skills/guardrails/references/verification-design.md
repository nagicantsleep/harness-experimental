# Verification Design

Source: Lauren Tan (@poteto) talk and workshop, pstack `create-verification-skill`.
Items marked `[ADDED]` are design extensions.

## Principle

Without a verification skill, "you are the verifier": the agent changes code,
you open a local build, copy a screenshot, and the agent guesses again. You
become the bottleneck. Verification "closes the loop. It doesn't guarantee
your agent writes good code but at least correct code."

Code review narrows to examining verification artifacts (video, screenshot,
diagram, formal verification) rather than reading code line by line.

## Evidence Standards

1. Use real user paths, not internal setters or test-only endpoints.
2. Record actions and resulting state, not only the final screen.
3. Check side effects (files written, rows inserted, messages sent) alongside
   visible output.
4. Mock only at production boundaries that already isolate external systems.
5. For dry-run modes, verify by observation what was actually skipped.
6. Cleanup removes only instances and scratch. Never delete evidence. Only
   kill processes you started.
7. For bug fixes, reproduce the bug on the baseline first, then rerun the
   same scenario after the fix.

## Verdict (three states) `[ADDED]`

- **PASS**: scenario completed, all expectations met, no unexpected errors.
- **FAIL**: scenario completed but results are wrong (real bug or regression).
- **BLOCKED**: cannot conclude (missing fixture, broken environment, stale
  selector). BLOCKED must never be promoted to PASS. Weakening criteria or
  fixtures to achieve PASS is prohibited.

## Verification Recipes by Surface

| Surface | Control method | Notes |
| --- | --- | --- |
| Web / Electron | Playwright or CDP; trace, screenshot, console. Locators use role/label/testid. | Reuse existing Playwright/Cypress specs when available. |
| CLI / TUI | PTY/tmux: send keystrokes, read transcript, check exit code. | |
| HTTP API | HTTP client + check DB/queue/log. | |
| Godot | `godot --headless --import`, `--check-only`, scene smoke test via SceneTree script. | Screenshot via xvfb + opengl3. |
| .NET | `dotnet build -warnaserror`, `dotnet test`, host app with test server. | |
| Mobile | iOS Simulator (`xcrun simctl`), Android emulator (`adb`). | Mentioned by Lauren but recipes are reference-only. |

Do not write a new driver when the repo already has one.

## Feature Map

A sitemap of features from the user's perspective. Each feature has a file
describing: name in user language, how to reach it, how to control it with
a harness (stable selectors), prerequisites, evidence expectations, and
gotchas.

Template: `docs/templates/feature-map-index.md` and
`docs/templates/feature-map-entry.md`.

Requirements:
- Use stable selectors: ARIA roles, test IDs, route paths. Never use
  coordinates, CSS hashes, child indices, or DOM position.
- PRs that change routes, selectors, contracts, or state machines must update
  the Feature Map in the same commit.

## Skill Evaluation

Eval = unit test for a skill. Each time a skill is revised, rerun its evals.

### Process (verified: workshop + pstack)

1. **Frame**: state the variant being tested and what behavior counts as
   success. Write a rubric (3-6 specific criteria) for the judge only.
2. **Clean environment**: each worker gets its own directory with a neutral
   project name. Forbidden words in paths/files/prompts the worker sees:
   `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`,
   `benchmark`, `candidate`, `arena`.
3. **Organic prompt**: write like a real user stating a goal. Do not reveal
   what is being measured.
4. **Run N workers in parallel**, preferably across different models.
5. **Blind judge** using a model from a different family. Judge sees
   anonymized outputs, not model names.
6. **Verify from transcript**: check which files the worker actually read,
   not its self-report.
7. **Human review**: read all outputs and compare with judge verdicts.
   Disagreement indicates model bias or ambiguous rubric.
8. **Hill-climb**: iteratively revise the skill until eval scores meet
   the target.

### Additional structure `[ADDED]`

- Three fixture groups for verification skills: `broken` (system is broken,
  skill should report FAIL), `working` (system works, skill should report
  PASS), `missing-prereq` (environment incomplete, skill should report
  BLOCKED honestly).
- Holdout cases: kept outside the skill author's view, run last to detect
  overfitting.
- Budget: set a maximum number of improvement rounds per session. Stop when
  exhausted and report actual metrics.

Template: `docs/templates/skill-eval-rubric.md`.
