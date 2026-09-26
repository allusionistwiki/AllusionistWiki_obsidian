# _commit.ps1  vault commit helper (ASCII-only, no mojibake)
# Self-locating: the repo root is derived from this script's own location
# (tools/ lives inside the vault, so repo root = parent of tools/).
# No hardcoded machine paths; safe to commit to the public repo.
# Message is passed via -MsgFile (UTF-8) to avoid console mojibake.
# After committing it AUTO-PUSHES to the GitHub remote ($Remote:$Branch,
# default obs:main), fast-forward only (never --force). Use -NoPush to
# commit locally without pushing.
# Manual run (no popup):
#   cd <vault>/tools
#   & { Set-ExecutionPolicy -Scope Process Bypass; .\_commit.ps1 -All -MsgFile ..\_msg.txt }
param(
    [string]$Message = "wiki: update",
    [string]$MsgFile,
    [string[]]$Paths,
    [switch]$All,
    [string]$Remote = 'obs',
    [string]$Branch = 'main',
    [switch]$NoPush
)
# git not on PATH by default in this harness session
if (-not ($env:Path -like '*Git\cmd*')) { $env:Path += ';C:\Program Files\Git\cmd' }

if ($MsgFile) { $Message = (Get-Content -Path $MsgFile -Raw -Encoding UTF8).TrimEnd() }
# repo root = parent of this script's directory (tools/ -> vault root)
$repo = Split-Path -Parent $PSScriptRoot

if ($All)      { git -C $repo add -A }
elseif ($Paths) { git -C $repo add @Paths }
else            { Write-Host "ERROR: specify -All or -Paths"; exit 1 }

# commit only when something is staged (re-runs on a clean tree still push below)
$staged = @(git -C $repo diff --cached --name-only)
if ($staged.Count -gt 0) {
    git -C $repo commit -m $Message
} else {
    Write-Host "nothing staged; skipping commit"
}

# auto-push (fast-forward only). If the remote moved, this fails safely without force.
if (-not $NoPush) {
    git -C $repo push $Remote "HEAD:$Branch"
    if ($LASTEXITCODE -ne 0) { Write-Host "PUSH FAILED: fetch obs and rebase/merge before pushing (no --force)."; exit 1 }
}
