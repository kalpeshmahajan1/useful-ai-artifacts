# Shared helpers (dot-source). Windows PowerShell 5.1 and PowerShell 7 compatible.
$ErrorActionPreference = 'Stop'
$script:Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$script:Py   = Join-Path $script:Root 'scripts\python'

function Get-FwConfig { Get-Content (Join-Path $script:Root 'framework.config.json') -Raw | ConvertFrom-Json }

function Get-PythonCommand {
    foreach ($c in 'python', 'py', 'python3') { if (Get-Command $c -ErrorAction SilentlyContinue) { return $c } }
    throw 'Python 3.8+ not found on PATH. Install Python and re-run.'
}

function Invoke-Py {
    param([string]$Script, [string[]]$Arguments)
    $py = Get-PythonCommand
    & $py (Join-Path $script:Py $Script) @Arguments | Out-Host
    return $LASTEXITCODE
}
