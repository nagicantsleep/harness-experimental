# Design

## Domain Model

No durable-layer domain model changes are required. Intake, story, decision,
backlog, and trace records remain unchanged.

The platform label set expands to include:

```text
windows-x64 -> x86_64-pc-windows-msvc -> harness-cli-windows-x64.exe
```

## Application Flow

CLI command behavior remains unchanged. Decision verification still runs the
stored `verify_command`, but shell selection becomes platform-aware:

- Unix: `sh -c <command>`.
- Windows: `%COMSPEC% /C <command>`, falling back to `cmd.exe /C`.

## Interface Contract

Existing POSIX command examples remain valid:

```bash
scripts/bin/harness-cli <command>
```

Windows PowerShell users receive a native executable path:

```powershell
.\scripts\bin\harness-cli.exe <command>
```

Release artifacts become:

```text
harness-cli-macos-arm64
harness-cli-macos-x64
harness-cli-linux-x64
harness-cli-linux-arm64
harness-cli-windows-x64.exe
```

Each artifact keeps a sibling `.sha256` checksum.

## Data Model

No SQLite schema changes.

## UI / Platform Impact

Windows becomes a supported CLI platform for source execution, release builds,
and installer usage. macOS and Linux continue to use the existing Bash script.

## Observability

No new telemetry. Story proof should capture local Windows test output and
release workflow validation once a tag build runs.

## Alternatives Considered

1. Require Windows users to use WSL. Rejected because this keeps Windows as an
   unsupported indirect path and does not help PowerShell-based agents.
2. Publish a Windows binary but no installer. Rejected because the Harness
   operating model expects repository-local setup with a stable CLI path.
3. Rename all artifacts to include extensions. Rejected because that would churn
   existing macOS/Linux release contracts.
