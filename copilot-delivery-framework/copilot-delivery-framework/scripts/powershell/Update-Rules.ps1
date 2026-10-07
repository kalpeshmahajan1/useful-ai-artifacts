<#
.SYNOPSIS  After editing rules: lint -> compile instruction blocks -> run script tests.
#>
. (Join-Path $PSScriptRoot '_Common.ps1')
Push-Location $script:Root
try {
    $fail = 0
    if ((Invoke-Py 'lint_rules.py' @('--quiet')) -ne 0) { $fail = 1 }
    if ((Invoke-Py 'compile_instructions.py' @()) -ne 0) { $fail = 1 }
    $py = Get-PythonCommand
    & $py -m unittest discover -s tests -v 2>&1 | Select-Object -Last 4
    if ($LASTEXITCODE -ne 0) { $fail = 1 }
    if ($fail) { Write-Host 'Update-Rules FAILED' -ForegroundColor Red; exit 1 }
    Write-Host 'Rules OK. Review the diff, then commit through a PR (architect approval).' -ForegroundColor Green
} finally { Pop-Location }
