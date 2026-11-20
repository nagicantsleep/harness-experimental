# Evolution Loop

Source: synthesized from pstack `/correct` and `/reflect` skills, Lauren Tan's
talk principle "every time you correct an agent, make it deterministic," and
workshop guidance on observing agent behavior. Specific thresholds and
formatting are `[ADDED]`.

## Five-Step Checklist

Use this after each PR or agent correction. The goal is to escalate recurring
agent mistakes into deterministic guards that prevent the class of error from
recurring.

```text
1. OBSERVE    What did the agent get wrong?
              (Guessed without reading code / crossed a layer boundary /
              added a hack with a justifying comment / skipped verification /
              used a banned API)
              Evidence (commit, file:line, transcript): ______
              Has this happened >= 2 times? (If not: log it and watch.
              If yes: continue.)

2. CLASSIFY   Choose the HIGHEST FEASIBLE tier (stop at the first "yes"):
              [ ] T1  Can the design/directory/API be changed so the mistake
                      cannot be expressed? -> do it.
              [ ] T2  Can a static check (type/lint/dep graph/behavior test)
                      catch it with a "FIX:" message? -> do it.
              [ ] T3  Does it need running the app / a state invariant?
                      -> extend verification skill, Feature Map, PBT, or
                      TLA+.
              [ ] T4  Is it purely judgment/method? -> revise skill/playbook
                      and add one eval case.
              Record in the rule table: rule <-> enforcement mechanism.

3. CLEAN UP   Immediately after adding a rule: find and fix all existing
              violations (or baseline + schedule reduction). Do not leave
              bad patterns as bait for agents to copy.

4. MEASURE    a) The new rule fails on a real past violation (test) and
                 passes on a valid case.
              b) If a skill/playbook changed: run eval. Did agent behavior
                 actually change? (blind judge, different model family)
              c) CI passes with the same commands as local.

5. RETIRE     Cross off the manual review item that was just automated.
              Delete prose in AGENTS.md that the new guard makes redundant.
```

## Step-by-Step Rationale

1. **Observe.** Start by reading tool calls and thinking blocks to see where
   the agent actually failed, not just the result. A class of error counts
   after the second occurrence.

2. **Classify.** The order (architecture -> type -> lint with FIX message ->
   behavior test -> prose) matches pstack's `/correct` escalation. One layer
   at a time.

3. **Clean up.** "Start with a lint rule to prevent new occurrences ... and
   then clean up those old patterns." Use `--update-baseline` only as a
   stepping stone.

4. **Measure.** "Prove each new check fails on a real past mistake." For
   skills, use the eval process from the verification reference.

5. **Retire.** The end state: "at some point there's nothing left to review
   and agents can merge most of their own PRs." This is only safe after the
   lower tiers are solid.

## Rule Table

Maintain a mapping of rules to their enforcement mechanism in the consumer
repository. Template: `docs/templates/rule-table.md`.

When correcting an agent again: if the rule already exists but has no
enforcement, that is a repeat. Escalate the enforcement tier in the same
change. Remove a rule when the class of error can no longer occur.
