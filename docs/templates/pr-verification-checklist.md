## Why

<one or two sentences stating the change goal>

## What changed

<summary; keep the PR small, atomic, and easy to revert>

## Verification evidence (required for behavior changes)

- Verdict: `PASS` | `FAIL` | `BLOCKED` (merge only on `PASS`)
- Skill used: `verify-<app>`; Feature Map: `docs/feature-map/<feature>.md`
- Verified commit: `<sha>`
- Bug fix: artifact **before** the fix (reproduction) → <path/link>; **after**
  the fix, same scenario → <path/link>
- Artifacts (screenshot / video / trace / log / HTTP / DB): <link or
  `.artifacts/<run-id>/`>
- State chart / TLA+ / PBT (if a complex state module): <link>
- Not proven by this run: <environment differences, uncovered surfaces>

## Harness

- [ ] Architecture / slop gate green with the same command as CI: `<command>`
- [ ] No bare lint/type suppressions without a ticket or link
- [ ] No justifying comments; no timer/sleep used to "wait for state"
- [ ] Feature Map updated in the same commit if routes/selectors/contracts/
      state machines changed
- [ ] Baseline did not increase (`.harness/baseline.json`)
- [ ] If this PR fixes a recurring agent mistake: evolution loop applied
      (observe → classify → clean up → measure → retire); tier ______;
      rule/test added ______; old patterns cleaned ☐
- [ ] Manual review item that was just automated has been removed from the
      review checklist ☐
