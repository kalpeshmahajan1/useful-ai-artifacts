<#
.SYNOPSIS
  Normalizes any review target (PR, diff, branch, staged, files, list file...) into .copilot-review/ for the reviewer agent.
.EXAMPLE
  pwsh scripts/Get-ReviewTarget.ps1 -Mode PR -Value 482
  pwsh scripts/Get-ReviewTarget.ps1 -Mode Staged
  pwsh scripts/Get-ReviewTarget.ps1 -Mode Branch -Value feature/x -Base develop
  pwsh scripts/Get-ReviewTarget.ps1 -Mode BranchDiff -Base release/1.0 -Value feature/x   # direct A..B
  pwsh scripts/Get-ReviewTarget.ps1 -Mode Files -Path src/A.cs,src/B.cs
  pwsh scripts/Get-ReviewTarget.ps1 -Mode FileList -Value files-to-review.txt
  pwsh scripts/Get-ReviewTarget.ps1 -Mode Folder -Value src/Services
  pwsh scripts/Get-ReviewTarget.ps1 -Mode Range -Value abc123..def456
  pwsh scripts/Get-ReviewTarget.ps1 -Mode Commit -Value abc123
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [ValidateSet('PR','WorkingDiff','Staged','Branch','BranchDiff','Range','Commit','Files','FileList','Folder')]
  [string]$Mode,
  [string]$Value,
  [string]$Base,
  [string[]]$Path,
  [int]$ContextLines = 25,
  [string]$OutDir = '.copilot-review'
)
$ErrorActionPreference = 'Stop'

$ExcludePatterns = @('\.min\.(js|css)$','package-lock\.json$','yarn\.lock$','(^|/)(bin|obj|node_modules|dist|\.angular|packages)/',
  '\.Designer\.cs$','\.g\.cs$','\.generated\.','\.(png|jpg|jpeg|gif|ico|dll|exe|pdb|zip|dcm|woff2?|ttf|snk|pfx)$')
$FolderExt = @('.cs','.ts','.html','.scss','.css','.js','.sql','.cpp','.h','.hpp','.c','.xml','.json','.config','.xaml','.cshtml')

function Invoke-Git([string[]]$GitArgs) {
  $out = & git @GitArgs 2>&1
  if ($LASTEXITCODE -ne 0) { throw "git $($GitArgs -join ' ') failed: $out" }
  return $out
}
function Test-Excluded([string]$p) {
  $n = $p -replace '\\','/'
  foreach ($rx in $ExcludePatterns) { if ($n -match $rx) { return $true } }
  return $false
}
function Get-DefaultBase {
  foreach ($c in @('origin/develop','origin/main','origin/master','develop','main','master')) {
    & git rev-parse --verify --quiet $c *> $null
    if ($LASTEXITCODE -eq 0) { return $c }
  }
  throw 'Could not detect a base branch; pass -Base.'
}
function Parse-NameStatus($lines) {
  foreach ($l in $lines) {
    if (-not $l) { continue }
    $parts = "$l" -split "`t"
    $st = $parts[0].Substring(0,1)
    $p = $parts[$parts.Length-1]
    [pscustomobject]@{ path = $p; status = $st }
  }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$files = @(); $diffText = $null; $reviewType = 'diff'; $meta = @{}; $head = $null; $baseUsed = $null

switch ($Mode) {
  'PR' {
    if (-not $Value) { throw '-Value (PR number or URL) required' }
    $json = gh pr view $Value --json number,title,body,baseRefName,headRefName,files,url,author | ConvertFrom-Json
    $diffText = (gh pr diff $Value) -join "`n"
    $files = $json.files | ForEach-Object { [pscustomobject]@{ path = $_.path; status = 'M' } }
    $baseUsed = $json.baseRefName; $head = $json.headRefName
    $meta = @{ prNumber = $json.number; title = $json.title; url = $json.url; author = $json.author.login; body = $json.body }
    # PR diff from gh has default context; fine. For full context, run: gh pr checkout <n>
  }
  'WorkingDiff' { $diffText = (Invoke-Git @('diff','HEAD',"-U$ContextLines")) -join "`n"; $files = Parse-NameStatus (Invoke-Git @('diff','HEAD','--name-status')); $baseUsed='HEAD'; $head='working tree' }
  'Staged'      { $diffText = (Invoke-Git @('diff','--cached',"-U$ContextLines")) -join "`n"; $files = Parse-NameStatus (Invoke-Git @('diff','--cached','--name-status')); $baseUsed='HEAD'; $head='index' }
  'Branch' {
    $baseUsed = if ($Base) { $Base } else { Get-DefaultBase }
    $head = if ($Value) { $Value } else { (Invoke-Git @('rev-parse','--abbrev-ref','HEAD')) -join '' }
    $range = "$baseUsed...$head"   # merge-base diff = what the branch introduces
    $diffText = (Invoke-Git @('diff',$range,"-U$ContextLines")) -join "`n"; $files = Parse-NameStatus (Invoke-Git @('diff',$range,'--name-status'))
  }
  'BranchDiff' {
    if (-not $Base -or -not $Value) { throw 'BranchDiff needs -Base <branchA> and -Value <branchB>' }
    $baseUsed = $Base; $head = $Value; $range = "$Base..$Value"
    $diffText = (Invoke-Git @('diff',$range,"-U$ContextLines")) -join "`n"; $files = Parse-NameStatus (Invoke-Git @('diff',$range,'--name-status'))
  }
  'Range' {
    if (-not $Value) { throw '-Value required (e.g. a..b)' }
    $baseUsed = $Value; $head = $Value
    $diffText = (Invoke-Git @('diff',$Value,"-U$ContextLines")) -join "`n"; $files = Parse-NameStatus (Invoke-Git @('diff',$Value,'--name-status'))
  }
  'Commit' {
    if (-not $Value) { throw '-Value (commit sha) required' }
    $baseUsed = "$Value^"; $head = $Value
    $diffText = (Invoke-Git @('show','--format=',"-U$ContextLines",$Value)) -join "`n"
    $files = Parse-NameStatus (Invoke-Git @('show','--format=','--name-status',$Value))
  }
  'Files' {
    if (-not $Path) { throw '-Path required' }
    $reviewType = 'full'; $files = $Path | ForEach-Object { [pscustomobject]@{ path = $_; status = 'F' } }
  }
  'FileList' {
    if (-not $Value -or -not (Test-Path $Value)) { throw "-Value must be an existing list file (got '$Value')" }
    $reviewType = 'full'
    $files = Get-Content $Value | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith('#') } |
             ForEach-Object { [pscustomobject]@{ path = $_; status = 'F' } }
  }
  'Folder' {
    if (-not $Value -or -not (Test-Path $Value)) { throw "-Value must be an existing folder (got '$Value')" }
    $reviewType = 'full'
    $files = Get-ChildItem -Path $Value -Recurse -File | Where-Object { $FolderExt -contains $_.Extension.ToLower() } |
             ForEach-Object { [pscustomobject]@{ path = (Resolve-Path -Relative $_.FullName) -replace '^\.[\\/]',''; status = 'F' } }
  }
}

$kept = @(); $skipped = @()
foreach ($f in $files) {
  $p = ($f.path -replace '\\','/')
  if (Test-Excluded $p) { $skipped += [pscustomobject]@{ path = $p; reason = 'generated/binary/vendor' }; continue }
  if ($f.status -eq 'D') { $skipped += [pscustomobject]@{ path = $p; reason = 'deleted' }; continue }
  if ($reviewType -eq 'full' -and -not (Test-Path $p)) { $skipped += [pscustomobject]@{ path = $p; reason = 'not found' }; continue }
  $kept += [pscustomobject]@{ path = $p; status = $f.status; reviewType = $reviewType }
}

if ($diffText) { Set-Content -Path (Join-Path $OutDir 'target.diff') -Value $diffText -Encoding UTF8 }
elseif (Test-Path (Join-Path $OutDir 'target.diff')) { Remove-Item (Join-Path $OutDir 'target.diff') }
Set-Content -Path (Join-Path $OutDir 'files.txt') -Value ($kept.path) -Encoding UTF8

$changed = 0
if ($diffText) { $changed = ($diffText -split "`n" | Where-Object { $_ -match '^[+-](?![+-])' }).Count }
$manifest = [ordered]@{
  mode = $Mode; value = $Value; base = $baseUsed; head = $head; reviewType = $reviewType
  generatedAt = (Get-Date).ToString('s'); changedLines = $changed
  files = $kept; skipped = $skipped; meta = $meta
  diffPath = $(if ($diffText) { "$OutDir/target.diff" } else { $null })
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $OutDir 'manifest.json') -Encoding UTF8
Write-Host "Review target ready: $($kept.Count) files ($reviewType), $($skipped.Count) skipped, $changed changed lines -> $OutDir/manifest.json"
