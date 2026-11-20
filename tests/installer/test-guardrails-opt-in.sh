#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
installer="$root/scripts/install-harness.sh"
manifest="$root/scripts/guardrails-install-files.txt"
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT

cargo build --quiet --manifest-path "$root/Cargo.toml" -p harness --locked
core_binary="$root/target/debug/harness"

install() {
  HARNESS_CORE_BINARY="$core_binary" "$installer" "$@"
}

# Cause: no guardrails flag. Effect: the neutral core contains no guardrails
# pack and the optional manifest remains outside the core declaration.
default_target="$temp/default"
install --directory "$default_target" --yes >"$temp/default.out"
grep -Fq 'Guardrails: excluded' "$temp/default.out"
[[ ! -e "$default_target/.agents/skills/guardrails" ]]
! grep -Fq '.agents/skills/guardrails/' \
  "$root/scripts/harness-install-files.txt"
[[ ! -f "$default_target/docs/templates/rule-table.md" ]]
[[ ! -f "$default_target/docs/templates/verify-app-skill.md" ]]

# Cause: explicit guardrails flag. Effect: every optional-manifest member is
# installed, but metadata still requires explicit skill invocation.
opt_in_target="$temp/opt-in"
install --directory "$opt_in_target" --with-guardrails --yes \
  >"$temp/opt-in.out"
grep -Fq 'Guardrails: included (explicit opt-in)' "$temp/opt-in.out"
while IFS= read -r relative || [[ -n "$relative" ]]; do
  relative="${relative%$'\r'}"
  case "$relative" in
    ""|\#*) continue ;;
  esac
  [[ -f "$opt_in_target/$relative" ]]
done <"$manifest"
grep -Fq 'allow_implicit_invocation: false' \
  "$opt_in_target/.agents/skills/guardrails/agents/openai.yaml"
grep -Fq 'Use only when the user explicitly invokes' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq 'inverted-pyramid' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq 'baseline ratchet' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq 'Do not infer consumer policy' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq '$encode-invariant' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq '$improve-harness' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq '$onboard-repository' \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md"
grep -Fq 'Language-agnostic architecture and slop gate' \
  "$opt_in_target/.agents/skills/guardrails/tools/check_architecture.py"
grep -Fq '"fix"' \
  "$opt_in_target/.agents/skills/guardrails/tools/harness.config.template.json"
grep -Fq 'Pyramid tier' \
  "$opt_in_target/docs/templates/rule-table.md"
grep -Fq 'Feature Map' \
  "$opt_in_target/docs/templates/feature-map-index.md"
grep -Fq 'PASS' \
  "$opt_in_target/docs/templates/verify-app-skill.md"
grep -Fq 'BLOCKED' \
  "$opt_in_target/docs/templates/verify-app-skill.md"
grep -Fq 'different family' \
  "$opt_in_target/docs/templates/skill-eval-rubric.md"
grep -Fq 'Verification evidence' \
  "$opt_in_target/docs/templates/pr-verification-checklist.md"

# A later normal merge is non-activation, not removal.
before=$(shasum -a 256 \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md" | awk '{print $1}')
install --directory "$opt_in_target" --merge --yes >"$temp/reinstall.out"
after=$(shasum -a 256 \
  "$opt_in_target/.agents/skills/guardrails/SKILL.md" | awk '{print $1}')
[[ "$before" == "$after" ]]
grep -Fq 'Guardrails: excluded' "$temp/reinstall.out"

# PowerShell exposes the same named selection and consumes the same manifest.
grep -Fq '[switch]$WithGuardrails' "$root/scripts/install-harness.ps1"
grep -Fq \
  '$script:GuardrailsPayloadManifest = "scripts/guardrails-install-files.txt"' \
  "$root/scripts/install-harness.ps1"

# Decision record exists and is indexed.
grep -Fq '0029' "$root/docs/decisions/README.md"
grep -Fq 'Guardrails Opt-In Payload' \
  "$root/docs/decisions/0029-guardrails-opt-in-payload.md"

echo "guardrails default exclusion and explicit opt-in passed"
