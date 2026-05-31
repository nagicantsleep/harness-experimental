# Exec Plan

## Goal

Add first-class Windows x64 support for the Harness CLI while preserving the
existing macOS and Linux installer and release contract.

## Scope

In scope:

- Add a `windows-x64` release artifact built from `x86_64-pc-windows-msvc`.
- Name the Windows artifact `harness-cli-windows-x64.exe` and publish a matching
  `.sha256` checksum.
- Add or document PowerShell installation and usage for Windows.
- Keep the POSIX installer working for macOS and Linux.
- Make decision verification use a platform shell instead of assuming `sh` on
  Windows.
- Update validation evidence for Windows source execution and release wiring.

Out of scope:

- Windows arm64 artifacts.
- MSI, winget, Homebrew, or package-manager distribution.
- Changing CLI commands or durable database schema.
- Replacing Bash-based installation for macOS/Linux.

## Risk Classification

Risk flags:

- Public contracts.
- Cross-platform.
- Existing behavior.
- Weak proof.

Hard gates:

- Changing the stable macOS/Linux install path.
- Weakening checksum verification.

## Work Phases

1. Confirm current release and installer platform assumptions.
2. Add a high-risk story packet for Windows CLI support.
3. Update Rust shell execution to work on Windows and Unix.
4. Add Windows artifact mapping to the release build script.
5. Add Windows x64 to the GitHub Actions release matrix.
6. Add PowerShell installer support and docs.
7. Run Rust tests and CLI smoke checks on the local Windows workspace.
8. Record proof status and trace evidence.

## Stop Conditions

Pause for human confirmation if:

- Windows support requires changing existing POSIX artifact names.
- Checksum verification cannot be kept for Windows.
- The release workflow cannot smoke the Windows artifact.
- The local Windows source build fails outside the known `sh` assumption.
