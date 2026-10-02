# Migrate Hermes config to VAEL on Windows (R-7). Copy-only, idempotent.
# Usage: powershell -File scripts\migrate-hermes-to-vael.ps1 [-NonInteractive] [-DryRun]
# Exit 0 on success/no-op, 1 on failure or refusal.
param(
  [switch]$NonInteractive,
  [switch]$DryRun,
  [string]$HomeDir = $HOME
)

$ErrorActionPreference = "Stop"
$localAppData = $env:LOCALAPPDATA
if ([string]::IsNullOrWhiteSpace($localAppData)) {
  $localAppData = Join-Path $HomeDir "AppData\Local"
}
$src = Join-Path $HomeDir ".hermes"
$dst = if (-not [string]::IsNullOrWhiteSpace($env:VAEL_CONFIG_DIR)) { $env:VAEL_CONFIG_DIR } else { $localAppData + "\vael" }
# POSIX-layout installs keep ~/.hermes even on Windows (Git Bash/WSL files).
if (-not (Test-Path -LiteralPath $src -PathType Container)) {
  $alt = Join-Path $localAppData "hermes"
  if (Test-Path -LiteralPath $alt -PathType Container) { $src = $alt }
}
if (-not (Test-Path -LiteralPath $src -PathType Container)) {
  Write-Output "Nothing to migrate: no Hermes config dir found."
  exit 0
}
if ($src -eq $dst) {
  Write-Output "Source and destination are the same ($src). Nothing to do."
  exit 0
}
if ((Test-Path -LiteralPath $dst -PathType Container) -and @(Get-ChildItem -LiteralPath $dst -Force).Count -gt 0) {
  Write-Error "$dst already exists and is not empty - refusing to overwrite."
  exit 1
}

$files = @(Get-ChildItem -LiteralPath $src -Recurse -File -Force -ErrorAction SilentlyContinue)
if ($DryRun) {
  Write-Output "[dry-run] Would copy $($files.Count) file(s): $src -> $dst"
  Write-Output "[dry-run] $src would be left untouched."
  exit 0
}
if (-not $NonInteractive) {
  $answer = Read-Host "Copy $($files.Count) file(s) from $src to $dst? [y/N]"
  if ($answer -notmatch '^(y|Y|yes|YES)$') {
    Write-Output "Aborted. Nothing copied."
    exit 1
  }
}
try {
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
} catch {
  Write-Error "Copy failed: $($_.Exception.Message)"
  exit 1
}
$missing = 0
foreach ($f in $files) {
  $rel = $f.FullName.Substring($src.Length).TrimStart('\', '/')
  if (-not (Test-Path -LiteralPath (Join-Path $dst $rel) -PathType Leaf)) {
    Write-Error "MISSING after copy: $rel"
    $missing++
  }
}
if ($missing -gt 0) {
  Write-Error "Verification failed ($missing file(s)). $src untouched."
  exit 1
}
Write-Output "Migrated $($files.Count) file(s): $src -> $dst"
Write-Output "$src was left untouched (rollback: unset VAEL_CONFIG_DIR or delete $dst)."
exit 0
