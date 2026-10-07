<#
.SYNOPSIS  Builds reports/scope.json for the reviewer agent and static checks.
.EXAMPLE   .\Get-ReviewScope.ps1 -Mode staged
.EXAMPLE   .\Get-ReviewScope.ps1 -Mode branch -Base origin/main
.EXAMPLE   .\Get-ReviewScope.ps1 -Mode files -Paths src\A.cs,src\b.ts
.EXAMPLE   .\Get-ReviewScope.ps1 -Mode pr -Pr 123
#>
param(
    [Parameter(Mandatory)][ValidateSet('staged','unstaged','working','branch','diff','files','list-file','file','pr')][string]$Mode,
    [string]$Base, [string]$Head = 'HEAD', [string[]]$Paths, [string]$ListFile, [string]$Pr
)
. (Join-Path $PSScriptRoot '_Common.ps1')
$a = @('--mode', $Mode)
if ($Base)     { $a += @('--base', $Base) }
if ($Head)     { $a += @('--head', $Head) }
if ($Paths)    { $a += @('--paths') + $Paths }
if ($ListFile) { $a += @('--list-file', $ListFile) }
if ($Pr)       { $a += @('--pr', $Pr) }
Push-Location $script:Root
try { exit (Invoke-Py 'review_scope.py' $a) } finally { Pop-Location }
