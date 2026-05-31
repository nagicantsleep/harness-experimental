# Validation

## Proof Strategy

The story is done when Windows source execution passes locally, release wiring
can build and smoke a Windows x64 artifact in GitHub Actions, and docs show both
PowerShell and existing `.sh` usage paths.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | `cargo test --workspace` passes on Windows after platform shell selection is fixed. |
| Integration | `cargo run -q -p harness-cli -- --help` and database commands run from PowerShell. |
| E2E | PowerShell installer downloads or installs docs plus `scripts/bin/harness-cli.exe` into a temp target and verifies checksum. |
| Platform | GitHub Actions builds and smokes `harness-cli-windows-x64.exe`; existing macOS/Linux matrix remains. |
| Performance | Not applicable. |
| Logs/Audit | Trace commands remain available after Windows install. |

## Fixtures

- Temporary Harness database path for CLI smoke tests.
- Temporary install target for PowerShell installer smoke tests.

## Commands

```powershell
cargo test --workspace
cargo run -q -p harness-cli -- --help
cargo run -q -p harness-cli -- init
cargo run -q -p harness-cli -- query stats
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-harness.ps1 -Directory <temp> -Yes
```

```bash
bash -n scripts/install-harness.sh
bash -n scripts/build-harness-cli-release.sh
scripts/build-harness-cli-release.sh --target x86_64-unknown-linux-gnu
```

## Acceptance Evidence

2026-05-31 local Windows workspace:

- `cargo test --workspace`: passed, 15 tests.
- `cargo fmt --check`: passed.
- `cargo run -q -p harness-cli -- --help`: passed and rendered
  `harness-cli.exe` usage.
- `cargo build --package harness-cli --release --target x86_64-pc-windows-msvc`:
  passed and built the Windows x64 release target locally.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-harness.ps1 -DryRun -Directory .\tmp-harness-install -Yes`:
  passed and resolved `harness-cli-windows-x64.exe` to
  `scripts/bin/harness-cli.exe`.
- Bash syntax check against CRLF-normalized script content passed for
  `scripts/install-harness.sh` and `scripts/build-harness-cli-release.sh`.

Known remaining proof gap:

- GitHub Actions has not yet run the updated `windows-x64` release matrix.
