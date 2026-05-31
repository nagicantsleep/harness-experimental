[CmdletBinding()]
param(
    [string]$Directory = $PWD.Path,
    [switch]$Yes,
    [switch]$Merge,
    [switch]$Force,
    [switch]$DryRun,
    [string]$SourceBaseUrl = $env:HARNESS_SOURCE_BASE_URL,
    [string]$CliBaseUrl = $env:HARNESS_CLI_BASE_URL,
    [string]$CliReleaseTag = $env:HARNESS_CLI_RELEASE_TAG
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host $Message
}

function Fail([string]$Message) {
    throw "Error: $Message"
}

function Resolve-TargetDirectory([string]$Path) {
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)
    if ($expanded.StartsWith("~")) {
        $expanded = Join-Path $HOME $expanded.Substring(1).TrimStart("/", "\")
    }
    $parent = Split-Path -Parent $expanded
    if ([string]::IsNullOrWhiteSpace($parent)) {
        $parent = "."
    }
    $parent = Resolve-Path $parent
    Join-Path $parent (Split-Path -Leaf $expanded)
}

function Get-SourceRoot {
    if ($PSCommandPath) {
        $candidate = Resolve-Path (Join-Path (Split-Path -Parent $PSCommandPath) "..")
        if ((Test-Path (Join-Path $candidate "AGENTS.md")) -and
            (Test-Path (Join-Path $candidate "docs/HARNESS.md"))) {
            return $candidate.Path
        }
    }
    return $null
}

function Get-ReleaseTag([string]$SourceRoot, [string]$SourceUrl) {
    if ($CliReleaseTag) {
        return $CliReleaseTag
    }

    $relative = "scripts/harness-cli-release-tag"
    if ($SourceRoot) {
        $tagPath = Join-Path $SourceRoot $relative
        if (Test-Path $tagPath) {
            return (Get-Content $tagPath | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") } | Select-Object -First 1).Trim()
        }
    }

    try {
        $tagText = Invoke-RestMethod -Uri "$SourceUrl/$relative"
        return (($tagText -split "`n") | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") } | Select-Object -First 1).Trim()
    } catch {
        return ""
    }
}

function Copy-HarnessFile([string]$Relative) {
    $target = Join-Path $TargetDir $Relative
    if ($Relative -eq ".gitignore" -and (Test-Path $target) -and -not $Force) {
        Merge-Gitignore $target
        return
    }

    if (Test-Path $target) {
        if ($Merge -and -not $Force) {
            Write-Step "skip     $Relative (merge keeps existing file)"
            $script:Skipped++
            return
        }
        if (-not $Force) {
            Write-Step "skip     $Relative (already exists)"
            $script:Skipped++
            return
        }
        if ($DryRun) {
            Write-Step "overwrite $Relative (backup first)"
        } else {
            $backup = Join-Path $BackupDir $Relative
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
            Copy-Item $target $backup -Force
            Write-SourceFile $Relative $target
            Write-Step "updated  $Relative"
        }
        $script:Updated++
        return
    }

    if ($DryRun) {
        Write-Step "create   $Relative"
    } else {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Write-SourceFile $Relative $target
        Write-Step "created  $Relative"
    }
    $script:Created++
}

function Write-SourceFile([string]$Relative, [string]$Target) {
    if ($SourceRoot) {
        $source = Join-Path $SourceRoot $Relative
        if (-not (Test-Path $source)) {
            Fail "Source file missing: $source"
        }
        Copy-Item $source $Target -Force
        return
    }

    Invoke-WebRequest -Uri "$SourceBaseUrl/$Relative" -OutFile $Target
}

function Merge-Gitignore([string]$Target) {
    $rules = @("harness.db", "harness.db-wal", "harness.db-shm", "scripts/bin/harness-cli", "scripts/bin/harness-cli.exe")
    $content = Get-Content $Target -ErrorAction SilentlyContinue
    $missing = $rules | Where-Object { $_ -notin $content }
    if (-not $missing) {
        Write-Step "skip     .gitignore (harness rules already present)"
        $script:Skipped++
        return
    }

    if ($DryRun) {
        Write-Step "update   .gitignore (append harness rules)"
    } else {
        Add-Content -Path $Target -Value ""
        Add-Content -Path $Target -Value "# Harness durable layer"
        Add-Content -Path $Target -Value $missing
        Write-Step "updated  .gitignore (appended harness rules)"
    }
    $script:Updated++
}

function Test-ProtectedPaths {
    $conflicts = @("AGENTS.md", "docs", "scripts") | Where-Object { Test-Path (Join-Path $TargetDir $_) }
    if (-not $conflicts) {
        return
    }
    if ($Merge -or $Force) {
        return
    }
    $joined = $conflicts -join ", "
    Fail "target already contains protected Harness paths: $joined. Re-run with -Merge or -Force."
}

function Install-HarnessCliBinary {
    $platform = "windows-x64"
    $binaryName = "harness-cli-$platform.exe"
    $target = Join-Path $TargetDir "scripts/bin/harness-cli.exe"
    $targetLabel = "scripts/bin/harness-cli.exe"

    if ((Test-Path $target) -and $Merge -and -not $Force) {
        Write-Step "skip     $targetLabel (merge keeps existing file)"
        $script:Skipped++
        return
    }

    if ($DryRun) {
        Write-Step "download $binaryName -> $targetLabel"
        Write-Step "verify   $binaryName.sha256"
        $script:Created++
        return
    }

    $tmp = New-Item -ItemType Directory -Force -Path (Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString()))
    try {
        $binaryTmp = Join-Path $tmp $binaryName
        $checksumTmp = Join-Path $tmp "$binaryName.sha256"
        Invoke-WebRequest -Uri "$CliBaseUrl/$binaryName" -OutFile $binaryTmp
        Invoke-WebRequest -Uri "$CliBaseUrl/$binaryName.sha256" -OutFile $checksumTmp
        $expected = ((Get-Content $checksumTmp | Select-Object -First 1) -split "\s+")[0].ToLowerInvariant()
        $actual = (Get-FileHash -Algorithm SHA256 $binaryTmp).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            Fail "Checksum mismatch for ${binaryName}: expected $expected, got $actual"
        }

        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        if (Test-Path $target) {
            if ($Force) {
                $backup = Join-Path $BackupDir $targetLabel
                New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
                Copy-Item $target $backup -Force
            }
            $script:Updated++
            Write-Step "updated  $targetLabel"
        } else {
            $script:Created++
            Write-Step "created  $targetLabel"
        }
        Copy-Item $binaryTmp $target -Force
        Write-Step "verified $targetLabel ($platform)"
    } finally {
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

$SourceRoot = Get-SourceRoot
if (-not $SourceBaseUrl) {
    $SourceBaseUrl = "https://raw.githubusercontent.com/hoangnb24/harness-experimental/main"
}
$SourceBaseUrl = $SourceBaseUrl.TrimEnd("/")

if (-not $CliBaseUrl) {
    $tag = Get-ReleaseTag $SourceRoot $SourceBaseUrl
    if ($tag -and $tag -ne "latest") {
        $CliBaseUrl = "https://github.com/hoangnb24/harness-experimental/releases/download/$tag"
    } else {
        $CliBaseUrl = "https://github.com/hoangnb24/harness-experimental/releases/latest/download"
    }
}
$CliBaseUrl = $CliBaseUrl.TrimEnd("/")

$TargetDir = Resolve-TargetDirectory $Directory
$BackupDir = Join-Path $TargetDir (".harness-backup/" + (Get-Date -Format "yyyyMMddHHmmss"))
$Created = 0
$Updated = 0
$Skipped = 0

if (-not [Environment]::Is64BitOperatingSystem) {
    Fail "Unsupported Harness CLI platform: Windows x86. Windows x64 is required."
}

if ($DryRun) {
    Write-Step "Dry run: no files will be written."
} elseif (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

Test-ProtectedPaths

if ($SourceRoot) {
    Write-Step "Harness source: $SourceRoot"
} else {
    Write-Step "Harness source: $SourceBaseUrl"
}
Write-Step "Harness CLI source: $CliBaseUrl"
Write-Step "Target project: $TargetDir"

$files = @(
    "AGENTS.md",
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/CONTEXT_RULES.md",
    "docs/FEATURE_INTAKE.md",
    "docs/GLOSSARY.md",
    "docs/HARNESS.md",
    "docs/HARNESS_BACKLOG.md",
    "docs/HARNESS_COMPONENTS.md",
    "docs/HARNESS_MATURITY.md",
    "docs/README.md",
    "docs/TEST_MATRIX.md",
    "docs/TRACE_SPEC.md",
    "docs/decisions/0001-harness-first-development.md",
    "docs/decisions/0002-post-spec-product-lifecycle.md",
    "docs/decisions/0003-generic-spec-intake-harness.md",
    "docs/decisions/0004-sqlite-durable-layer.md",
    "docs/decisions/0005-prebuilt-rust-harness-cli.md",
    "docs/decisions/README.md",
    "docs/product/README.md",
    "docs/stories/README.md",
    "docs/stories/backlog.md",
    "docs/templates/decision.md",
    "docs/templates/spec-intake.md",
    "docs/templates/story.md",
    "docs/templates/validation-report.md",
    "docs/templates/high-risk-story/design.md",
    "docs/templates/high-risk-story/execplan.md",
    "docs/templates/high-risk-story/overview.md",
    "docs/templates/high-risk-story/validation.md",
    "scripts/README.md",
    "scripts/schema/001-init.sql",
    ".gitignore"
)

foreach ($file in $files) {
    Copy-HarnessFile $file
}

Install-HarnessCliBinary

Write-Step ""
Write-Step "Done. Created: $Created, updated: $Updated, skipped: $Skipped."
if ($Force -and $Updated -gt 0 -and -not $DryRun) {
    Write-Step "Backups were written to: $BackupDir"
}
