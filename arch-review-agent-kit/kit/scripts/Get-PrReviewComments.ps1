<#
.SYNOPSIS
  Harvests PR review threads (with diff hunks, resolved/outdated state) via GitHub CLI for rule mining. Incremental.
.EXAMPLE
  pwsh scripts/Get-PrReviewComments.ps1 -Reviewer jdoe -Limit 50
  pwsh scripts/Get-PrReviewComments.ps1 -Reviewer jdoe -PrNumber 410,411,415
  pwsh scripts/Get-PrReviewComments.ps1 -IncludeAllReviewers -Limit 30 -Force
.NOTES
  Requires: gh CLI authenticated (gh auth login). Output: .github/review-knowledge/harvest/
#>
[CmdletBinding()]
param(
  [string]$Repo,
  [string[]]$Reviewer,
  [int[]]$PrNumber,
  [ValidateSet('merged','closed','all')][string]$State = 'merged',
  [int]$Limit = 50,
  [string]$OutDir = '.github/review-knowledge/harvest',
  [switch]$IncludeAllReviewers,
  [switch]$IncludeBots,
  [switch]$Force
)
$ErrorActionPreference = 'Stop'
if (-not $Reviewer -and -not $IncludeAllReviewers) { throw 'Pass -Reviewer <architect-login[,..]> or -IncludeAllReviewers.' }
if (-not $Repo) { $Repo = (gh repo view --json nameWithOwner | ConvertFrom-Json).nameWithOwner }
$owner, $name = $Repo.Split('/')
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$processedPath = Join-Path $OutDir 'processed-prs.json'
$processed = @()
if ((Test-Path $processedPath) -and -not $Force) { $processed = @(Get-Content $processedPath -Raw | ConvertFrom-Json) }

if (-not $PrNumber) {
  $stateArg = if ($State -eq 'all') { 'all' } else { $State }
  $PrNumber = gh pr list --repo $Repo --state $stateArg --limit $Limit --json number | ConvertFrom-Json | ForEach-Object { $_.number }
}
$todo = @($PrNumber | Where-Object { $Force -or ($processed -notcontains $_) })
Write-Host "PRs to harvest: $($todo.Count) (skipping $($PrNumber.Count - $todo.Count) already processed)"

$query = @'
query($owner:String!,$name:String!,$number:Int!){
  repository(owner:$owner,name:$name){
    pullRequest(number:$number){
      number title url mergedAt author{login}
      reviews(first:50){nodes{author{login} body state url}}
      reviewThreads(first:100){nodes{
        isResolved isOutdated path line originalLine
        comments(first:30){nodes{author{login} body createdAt diffHunk url}}
      }}
    }
  }
}
'@

$stamp = Get-Date -Format 'yyyyMMdd-HHmm'
$jsonl = Join-Path $OutDir "harvest-$stamp.jsonl"
$md    = Join-Path $OutDir "harvest-$stamp.md"
"# PR review harvest $stamp`nRepo: $Repo`n" | Set-Content $md -Encoding UTF8

function Test-Wanted($login) {
  if (-not $login) { return $false }
  if (-not $IncludeBots -and ($login -like '*[[]bot[]]' -or $login -like '*copilot*' -or $login -like '*sonar*')) { return $false }
  if ($IncludeAllReviewers) { return $true }
  return ($Reviewer -contains $login)
}

$threadCount = 0; $done = @()
foreach ($n in $todo) {
  try {
    $raw = gh api graphql -f query=$query -F owner=$owner -F name=$name -F number=$n | ConvertFrom-Json
  } catch { Write-Warning "PR #$n failed: $_"; continue }
  $pr = $raw.data.repository.pullRequest
  if (-not $pr) { continue }
  "## PR #$($pr.number) - $($pr.title)`n$($pr.url) | author: $($pr.author.login)`n" | Add-Content $md -Encoding UTF8

  foreach ($t in $pr.reviewThreads.nodes) {
    $cs = @($t.comments.nodes)
    if (-not ($cs | Where-Object { Test-Wanted $_.author.login })) { continue }
    $threadCount++
    $rec = [ordered]@{
      type='thread'; pr=$pr.number; prTitle=$pr.title; prUrl=$pr.url; path=$t.path; line=$t.line; originalLine=$t.originalLine
      isResolved=$t.isResolved; isOutdated=$t.isOutdated; diffHunk=$cs[0].diffHunk
      comments=@($cs | ForEach-Object { [ordered]@{ author=$_.author.login; body=$_.body; url=$_.url } })
    }
    ($rec | ConvertTo-Json -Depth 6 -Compress) | Add-Content $jsonl -Encoding UTF8

    $threadState = "resolved=$($t.isResolved), outdated=$($t.isOutdated)"
    "### $($t.path):$($t.line)  ($threadState)" | Add-Content $md -Encoding UTF8
    "``````diff`n$($cs[0].diffHunk)`n``````" | Add-Content $md -Encoding UTF8
    foreach ($c in $cs) { "- **$($c.author.login)**: $($c.body -replace "`r?`n",' ')  ($($c.url))" | Add-Content $md -Encoding UTF8 }
    "" | Add-Content $md -Encoding UTF8
  }
  foreach ($r in $pr.reviews.nodes) {
    if ($r.body -and (Test-Wanted $r.author.login)) {
      $rec = [ordered]@{ type='review-summary'; pr=$pr.number; prUrl=$pr.url; author=$r.author.login; state=$r.state; body=$r.body; url=$r.url }
      ($rec | ConvertTo-Json -Depth 4 -Compress) | Add-Content $jsonl -Encoding UTF8
      "- *Review ($($r.state))* **$($r.author.login)**: $($r.body -replace "`r?`n",' ')" | Add-Content $md -Encoding UTF8
    }
  }
  $done += $n
}
$all = @($processed) + @($done) | Sort-Object -Unique
ConvertTo-Json -InputObject @($all) | Set-Content $processedPath -Encoding UTF8
Write-Host "Harvested $threadCount threads from $($done.Count) PRs -> $md"
Write-Host "Next: in VS Code Copilot Chat run /learn-from-prs"
