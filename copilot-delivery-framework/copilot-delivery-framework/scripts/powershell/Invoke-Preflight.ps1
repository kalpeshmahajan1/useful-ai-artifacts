<#
.SYNOPSIS  Local quality gate: scope -> rule lint -> instruction freshness -> static checks -> (optional) build/tests/lint.
.DESCRIPTION
  Runs only what is configured/available and REPORTS what was skipped. A skipped step is never a pass.
  Configure paths.solution (.sln) and paths.frontend_dir in framework.config.json.
.EXAMPLE   .\Invoke-Preflight.ps1 -Mode staged
.EXAMPLE   .\Invoke-Preflight.ps1 -Mode branch -Base origin/main -Build -Test
#>
param(
    [ValidateSet('staged','unstaged','working','branch','diff')][string]$Mode = 'working',
    [string]$Base, [string]$Head = 'HEAD',
    [switch]$Build, [switch]$Test, [switch]$Frontend
)
. (Join-Path $PSScriptRoot '_Common.ps1')
$cfg = Get-FwConfig
$results = New-Object System.Collections.Generic.List[object]
function Add-Result($name, $status, $detail) { $results.Add([pscustomobject]@{ Step = $name; Status = $status; Detail = $detail }) }

Push-Location $script:Root
try {
    $reports = Join-Path $script:Root $cfg.paths.reports_dir
    New-Item -ItemType Directory -Force -Path $reports | Out-Null

    # 1 scope
    $sa = @('--mode', $Mode); if ($Base) { $sa += @('--base', $Base) }; if ($Head) { $sa += @('--head', $Head) }
    $rc = Invoke-Py 'review_scope.py' $sa
    Add-Result 'scope' ($(if ($rc -eq 0) {'ok'} else {'FAIL'})) "reports/scope.json"

    # 2 framework self-checks
    $rc = Invoke-Py 'lint_rules.py' @('--quiet');            Add-Result 'rules lint' ($(if ($rc -eq 0) {'ok'} else {'FAIL'})) ''
    $rc = Invoke-Py 'compile_instructions.py' @('--check');  Add-Result 'instructions up to date' ($(if ($rc -eq 0) {'ok'} else {'FAIL'})) 'run compile_instructions.py if stale'

    # 3 static checks on the scope
    $rc = Invoke-Py 'static_checks.py' @('--scope', (Join-Path $reports 'scope.json'), '--out', (Join-Path $reports 'static.json'))
    Add-Result 'static checks' ($(if ($rc -eq 0) {'ok'} else {'FAIL'})) 'reports/static.json (gate = blocker/major, certain/likely)'

    # 4 build (.NET Framework needs MSBuild from Visual Studio; located with vswhere)
    if ($Build) {
        $sln = $cfg.paths.solution
        if (-not $sln) { Add-Result 'build' 'SKIPPED' 'paths.solution not configured' }
        else {
            $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
            $msb = $null
            if (Test-Path $vswhere) { $msb = & $vswhere -latest -requires Microsoft.Component.MSBuild -find 'MSBuild\**\Bin\MSBuild.exe' | Select-Object -First 1 }
            if (-not $msb) { Add-Result 'build' 'SKIPPED' 'MSBuild not found (install Visual Studio Build Tools)' }
            else {
                & $msb $sln /restore /m /v:minimal /nologo /warnaserror-
                Add-Result 'build' ($(if ($LASTEXITCODE -eq 0) {'ok'} else {'FAIL'})) $sln
            }
        }
    } else { Add-Result 'build' 'SKIPPED' 'use -Build' }

    # 5 tests (vstest.console from Visual Studio, or dotnet test for SDK-style test projects)
    if ($Test) {
        if (Get-Command dotnet -ErrorAction SilentlyContinue) {
            if ($cfg.paths.solution) { & dotnet test $cfg.paths.solution --nologo --verbosity minimal; Add-Result 'tests' ($(if ($LASTEXITCODE -eq 0) {'ok'} else {'FAIL'})) 'dotnet test' }
            else { Add-Result 'tests' 'SKIPPED' 'paths.solution not configured' }
        } else { Add-Result 'tests' 'SKIPPED' 'dotnet CLI not found' }
    } else { Add-Result 'tests' 'SKIPPED' 'use -Test' }

    # 6 frontend lint/tests (uses the package.json scripts the team already has)
    if ($Frontend) {
        $fe = $cfg.paths.frontend_dir
        if (-not $fe -or -not (Test-Path $fe)) { Add-Result 'frontend' 'SKIPPED' 'paths.frontend_dir not configured' }
        else {
            Push-Location $fe
            try {
                $pkg = Get-Content package.json -Raw | ConvertFrom-Json
                if ($pkg.scripts.lint) { & npm run lint --silent; Add-Result 'frontend lint' ($(if ($LASTEXITCODE -eq 0) {'ok'} else {'FAIL'})) 'npm run lint' }
                else { Add-Result 'frontend lint' 'SKIPPED' 'no "lint" script' }
                if ($pkg.scripts.test) { & npm test --silent -- --watch=false; Add-Result 'frontend tests' ($(if ($LASTEXITCODE -eq 0) {'ok'} else {'FAIL'})) 'npm test' }
                else { Add-Result 'frontend tests' 'SKIPPED' 'no "test" script' }
            } finally { Pop-Location }
        }
    } else { Add-Result 'frontend' 'SKIPPED' 'use -Frontend' }
}
finally { Pop-Location }

$results | Format-Table -AutoSize | Out-String | Write-Host
$md = @('# Preflight', '', '| Step | Status | Detail |', '|---|---|---|') + ($results | ForEach-Object { "| $($_.Step) | $($_.Status) | $($_.Detail) |" })
Set-Content -Path (Join-Path $script:Root "$($cfg.paths.reports_dir)\preflight.md") -Value $md -Encoding UTF8
if ($results | Where-Object Status -eq 'FAIL') { Write-Host 'PREFLIGHT FAILED' -ForegroundColor Red; exit 1 }
Write-Host 'Preflight finished (SKIPPED steps were NOT run).' -ForegroundColor Green
