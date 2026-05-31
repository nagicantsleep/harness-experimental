# Overview

## Current Behavior

Harness CLI releases and installer paths support macOS and Linux only. The Rust
CLI can compile on Windows from source, but there is no supported Windows release
artifact, no PowerShell installer, and decision verification assumes `sh -c`.

The documented stable command path is POSIX-oriented:

```bash
scripts/bin/harness-cli <command>
```

## Target Behavior

Harness ships a Windows x64 prebuilt CLI artifact and documents native Windows
usage through PowerShell:

```powershell
.\scripts\bin\harness-cli.exe <command>
```

The existing macOS and Linux `.sh` installer path remains supported. Windows
users can install Harness with a PowerShell script that downloads, verifies, and
places the Windows CLI binary at `scripts/bin/harness-cli.exe`.

## Affected Users

- Humans installing Harness from Windows.
- Coding agents running in PowerShell on Windows workspaces.
- Maintainers publishing Harness CLI releases.
- Existing macOS and Linux users relying on the `.sh` installer.

## Affected Product Docs

- `README.md`
- `scripts/README.md`
- `docs/decisions/0005-prebuilt-rust-harness-cli.md`
- `docs/stories/epics/E01-durable-layer/US-002-rust-harness-cli/*`

## Non-Goals

- Do not replace the existing POSIX `.sh` installer.
- Do not require Windows users to install Rust for normal Harness usage.
- Do not add Windows arm64 release support in this story.
- Do not change the SQLite schema.
