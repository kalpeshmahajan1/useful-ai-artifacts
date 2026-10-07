<#
.SYNOPSIS  Enables the repo's pre-commit hook (static checks on staged changes). Opt-in, per clone.
#>
. (Join-Path $PSScriptRoot '_Common.ps1')
Push-Location $script:Root
try { git config core.hooksPath .githooks; Write-Host 'Hooks enabled (core.hooksPath = .githooks). Bypass in an emergency: git commit --no-verify (CI still gates).' }
finally { Pop-Location }
