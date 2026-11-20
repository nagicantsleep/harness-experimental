# Architecture and Lint Design

Source: Lauren Tan (@poteto) talk and workshop, pstack plugin. Items marked
`[ADDED]` are design extensions. `[TESTED]` means the prototype ran the tool.

## Rule Catalog

| ID | Tier | Blocks | Source | Rationale |
| --- | --- | --- | --- | --- |
| `layer-boundaries` | T2 | Lower layer imports higher layer (`domain` must not import `infra`/`ui`) | Verified: cross-boundary import bans in Dune. Layer names are `[ADDED]`. | Agents import by convenience; directory names provide context. |
| `process-boundary` | T1+T2 | Code in wrong process/thread (main/renderer, server/client, game logic/scene) | Verified: Dune electron-main/renderer split. | Wrong-side imports cause long tasks and jank. |
| `feature-isolation` | T1+T2 | Feature imports another feature's internals | `[ADDED]` from verified co-location principle. | "Shortest path is the best path": all feature code in one directory. |
| `no-circular` | T2 | Circular dependencies | `[ADDED]` | Detected by scout tools and dependency-cruiser. |
| `no-foot-gun-api` | T1/T2 | Dangerous APIs: `useEffect`, timers, `any`, `unsafe`, raw SQL in domain, `get_parent()` | Verified: `useEffect` and timer bans. | Allow only in framework wrappers. |
| `no-justifying-comments` | T2 | Comments that justify workarounds ("hack", "for now", "do not remove") | Verified: comments as escape hatches. | Agents use comments to legitimize patches. |
| `no-comments` (strict) | T2 | All comments outside an allow-list | Verified: Grok Bot bans ~99% of comments. | Old comments mislead; enable only after baselining. |
| `no-bare-suppression` | T2 | Lint/type suppressions without a ticket or link | `[ADDED]` (pstack comment-sicko treats suppressions as a smell). | Suppressions are another gate escape hatch. |
| `ratchet` | Process | Fail only on new violations when a pattern is widespread | Verified: `/correct` "fail only when a change adds more." | Allows immediate adoption on legacy repos. |

## Error Message Formula

`WHAT (the violation) — WHY (one sentence) — FIX (use what, where)`

Good messages:

- `domain must not import infra (src/domain/order.ts:1). FIX: define an interface in src/domain/ports, implement it in src/infra, wire in src/composition.`
- `Timers patch over timing problems and spread by copy-paste. FIX: subscribe to the event that signals the state, or model the wait as a state-machine transition.`
- `Comment justifies a workaround. FIX: delete it and fix the cause: rename, extract, or encode the invariant in a type.`

Requirements: (1) name the correct path using real repo paths; (2) do not
blame; (3) if no correct path exists, create it before enabling the rule
(otherwise agents will suppress); (4) `check_architecture.py` refuses to start
if a rule is missing `fix`.

## Tool Matrix by Stack

| Stack | Layer/dependency | Banned API (with message) | Comment/suppression | Notes |
| --- | --- | --- | --- | --- |
| TypeScript/JS | `dependency-cruiser` (`--output-type err-long`); or `eslint-plugin-boundaries` v7 | ESLint `no-restricted-syntax`/`no-restricted-imports` with message | Custom rule `no-justifying-comments`; `@eslint-community/eslint-plugin-eslint-comments`; `@typescript-eslint/ban-ts-comment` | `eslint-plugin-boundaries` needs `eslint-import-resolver-typescript`. |
| Python | `import-linter` (layers/forbidden/independence; message in contract `name`) | ruff `TID251` banned-api with `msg`; `ERA001`; `T201` | ruff `PGH003/004`, `RUF100` | Comment justification via `check_architecture.py`. |
| C#/.NET | `NetArchTest.Rules` in xUnit; or ArchUnitNET | `Microsoft.CodeAnalysis.BannedApiAnalyzers` + `BannedSymbols.txt` (`RS0030`) | `.editorconfig` severity + `TreatWarningsAsErrors` | `#pragma warning disable` via `check_architecture.py`. |
| Godot/GDScript | `check_architecture.py` with `layers` on `res://` paths | Regex: `get_parent()`, `get_node("/root/...")`, `create_timer`, `.connect("...")` | `gdlint` (gdtoolkit) | No standard import graph; uses `preload`/`load`/`extends`. |
| Go | `depguard` (`desc` is message) | `forbidigo` (`msg`) | `nolintlint` (`require-explanation`) | |
| Rust | Crate graph + `cargo deny` | `clippy.toml` `disallowed-methods/types` with `reason` | `allow_attributes_without_reason` | `[UNTESTED]` in prototype. |
| Any (fallback) | `check_architecture.py` | `banned` rules (regex + glob + `except`) | `comments`, `suppressions` sections | Regex/lexer-based; prefer native AST tools for precision. |

Prefer AST/compiler tools for exact rules. `check_architecture.py` is a
fallback net based on regex and a lightweight lexer; it can produce false
positives on complex constructs (nested template strings, macros). Measure
false-positive rates on the real repo before enabling CI gating.

## Baseline Ratchet Strategy

1. Run the gate and count violations per rule.
2. `check_architecture.py --update-baseline` freezes the counts.
3. CI fails only when violations exceed the baseline for a (rule, file) pair.
4. Sweep: small PRs reduce the baseline; never manually increase it.
5. When baseline reaches zero, delete the baseline file and enforce absolutely.

This matches: "start with a lint rule to prevent new occurrences ... and then
clean up those old patterns."

## Lint Starters (Reference)

Each stack section below describes tool installation and initial config. These
are starting points, not installed files. The consumer must adapt them to their
actual architecture.

### TypeScript

Use ESLint 9 flat config. Key packages: `typescript-eslint`,
`eslint-plugin-boundaries` (with `eslint-import-resolver-typescript`),
`dependency-cruiser`. Define layers in `eslint.config.mjs` using boundaries
plugin `elements` and `rules`. Add `no-restricted-syntax` entries for timers
(`setTimeout`, `requestAnimationFrame`, `requestIdleCallback`) and
`useEffect` with FIX messages pointing to framework alternatives.

### Python

Use ruff for speed. Configure `TID251` banned-api entries with `msg` fields.
Use `import-linter` for layer contracts. Three contract types cover most
architectures: `layers` (ordered dependency), `forbidden` (specific bans),
`independence` (features must not import each other).

### .NET

Use `BannedApiAnalyzers` NuGet package with a `BannedSymbols.txt` file.
Architecture tests use `NetArchTest.Rules` in xUnit with clear FIX messages
in assertion failures. Enable `TreatWarningsAsErrors` in `Directory.Build.props`.

### Go and Rust

Go: `golangci-lint` v2 with `depguard` for import boundaries and `forbidigo`
for banned calls. Rust: workspace crate boundaries, `clippy.toml`
`disallowed-methods/types` with `reason`, `cargo deny` for dependency policy.

### Godot

GDScript has no standard import graph. Use `check_architecture.py` with
`layers` mapped to `res://` paths. Use `gdlint` (gdtoolkit) for style.
Ban `get_parent()`, `get_node("/root/...")`, bare `create_timer`, and
untyped signal connections.

## Limitations

- `check_architecture.py` comment lexer is approximate: handles strings,
  triple-quotes (Python/GDScript), and C-style block comments, but not
  heredocs or complex raw strings.
- TypeScript import resolution in `check_architecture.py` only understands
  declared `aliases` and relative paths.
- C# layer detection only sees `using` statements; fully-qualified references
  without `using` are invisible. Pair with `NetArchTest` for completeness.
