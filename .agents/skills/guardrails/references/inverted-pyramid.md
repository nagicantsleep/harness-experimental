# Inverted Pyramid: Investment Order

Source: Lauren Tan (@poteto), talk "All Code Is Slop (Except Mine)" (AI
Engineer CODE 2026), workshop (Vision Sabbat 2026-09), pstack plugin.
Items marked `[ADDED]` are design extensions, not from primary sources.

## Principle

Agent output quality depends on agent input quality. The codebase is one of
the largest inputs. Workarounds, anti-patterns, and tech debt look like
established patterns; agents copy them. Each time you correct an agent,
consider how to make that correction deterministic rather than adding another
prose rule.

## Four Tiers (widest at top, thinnest at bottom)

```text
T1  CODEBASE & ARCHITECTURE   Design APIs so incorrect usage cannot compile or
                               pass. Refactor, co-locate, remove foot-guns.
T2  STATIC & TEST              Lint, type system, compiler, dependency graph,
                               tests. Same deterministic layer as T1.
T3  VERIFICATION               Run the real app: runtime checks, formal
                               methods (TLA+/Lean), property-based testing.
T4  PROSE                      Rules, skills, AGENTS.md, playbooks. Only for
                               decisions requiring judgment.
```

T1 and T2 "constrain what agents can do and force them to do the right thing
by default." T3 finds bugs and checks "whether the agent understands your
goals and intent." T4 is the thinnest layer because agents can forget prose.

## Why Prose Is Not Enough

Rules, skills, and bugbot "are more soft ... your agents can still forget ...
I like to layer them but I don't like to rely on them." If only rules and
style guides guard the codebase, "it's only a matter of time before your
codebase looks like complete trash." Living in "code review land" where humans
read code to protect invariants is a process smell.

## Design Consequences

1. Every rule needs a "what enforces it" column. A rule with no enforcement
   is prose and must genuinely require judgment.
2. Lint and gate error messages teach the agent the fix at the exact moment
   of violation.
3. Invest in order: T1 then T2 then T3 then T4. Do not start with a long
   AGENTS.md.
4. Automating a loop that produces slop only produces more slop. Build the
   foundation (lint, cleanup, verification) before scaling automation.
5. `[ADDED]` Tier numbers are a classification tool. Do not force all four
   tiers for every issue; choose the highest feasible tier.

## Caveats (do not skip)

- Lauren works at an AI lab with effectively unlimited tokens. Not everyone
  should replicate her exact approach. She believes the results are achievable
  without excessive cost.
- It took approximately six months to reach the level of shipping thousands of
  PRs. Do not jump from one agent to thousands of cloud agents.
- Formal verification is "another layer, certainly not a silver bullet," still
  experimental. It has caught bugs but is not universally applicable.
