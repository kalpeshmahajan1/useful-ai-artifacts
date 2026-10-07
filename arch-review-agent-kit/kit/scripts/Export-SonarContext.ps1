<#
.SYNOPSIS
  Pulls your real SonarQube quality profile, quality gate and top recurring issues so the reviewer/generator use YOUR rules.
.EXAMPLE
  $env:SONAR_TOKEN = '<token>'
  pwsh scripts/Export-SonarContext.ps1 -SonarUrl https://sonar.contoso.com -ProjectKey my-viewer
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$SonarUrl,
  [Parameter(Mandatory)][string]$ProjectKey,
  [string]$Token = $env:SONAR_TOKEN,
  [string]$OutDir = '.github/review-knowledge/sonar',
  [int]$TopRules = 40
)
$ErrorActionPreference = 'Stop'
if (-not $Token) { throw 'Set $env:SONAR_TOKEN or pass -Token' }
$SonarUrl = $SonarUrl.TrimEnd('/')
$hdr = @{ Authorization = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Token}:")) }
function Get-Sonar($pathAndQuery) { Invoke-RestMethod -Uri "$SonarUrl$pathAndQuery" -Headers $hdr }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# 1) Active rules per quality profile
$profiles = (Get-Sonar "/api/qualityprofiles/search?project=$ProjectKey").profiles
$sb = [Text.StringBuilder]::new()
[void]$sb.AppendLine("# SonarQube active rules ($ProjectKey)`nGenerated $(Get-Date -Format s). Takes precedence over sonar-guidance.md.`n")
foreach ($p in $profiles) {
  [void]$sb.AppendLine("## $($p.language) - $($p.name) ($($p.activeRuleCount) rules)`n")
  [void]$sb.AppendLine('| Key | Name | Severity | Type |'); [void]$sb.AppendLine('|---|---|---|---|')
  $page = 1
  do {
    $r = Get-Sonar "/api/rules/search?qprofile=$($p.key)&activation=true&ps=500&p=$page&f=name,severity,type"
    foreach ($x in $r.rules) { [void]$sb.AppendLine("| $($x.key) | $($x.name -replace '\|','/') | $($x.severity) | $($x.type) |") }
    $page++
  } while (($page - 1) * 500 -lt $r.total)
  [void]$sb.AppendLine()
}
Set-Content (Join-Path $OutDir 'active-rules.md') $sb.ToString() -Encoding UTF8

# 2) Quality gate
$qg = Get-Sonar "/api/qualitygates/project_status?projectKey=$ProjectKey"
$g = [Text.StringBuilder]::new()
[void]$g.AppendLine("# Quality gate ($ProjectKey)`nStatus now: $($qg.projectStatus.status)`n`n| Metric | Comparator | Threshold |`n|---|---|---|")
foreach ($c in $qg.projectStatus.conditions) { [void]$g.AppendLine("| $($c.metricKey) | $($c.comparator) | $($c.errorThreshold) |") }
Set-Content (Join-Path $OutDir 'quality-gate.md') $g.ToString() -Encoding UTF8

# 3) Most frequent open issues = what this team actually trips on
$iss = Get-Sonar "/api/issues/search?componentKeys=$ProjectKey&resolved=false&ps=1&facets=rules"
$facet = ($iss.facets | Where-Object { $_.property -eq 'rules' }).values | Select-Object -First $TopRules
$t = [Text.StringBuilder]::new()
[void]$t.AppendLine("# Top recurring open Sonar issues ($ProjectKey)`nReviewer: prioritize predicting these.`n`n| Rule | Open issues |`n|---|---|")
foreach ($f in $facet) { [void]$t.AppendLine("| $($f.val) | $($f.count) |") }
Set-Content (Join-Path $OutDir 'top-issues.md') $t.ToString() -Encoding UTF8
Write-Host "Sonar context written to $OutDir (active-rules.md, quality-gate.md, top-issues.md)"
