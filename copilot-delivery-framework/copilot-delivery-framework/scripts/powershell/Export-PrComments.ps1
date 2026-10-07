<#
.SYNOPSIS  Exports PR review comments, PR list and reviews via GitHub CLI for rule mining and baseline metrics.
.DESCRIPTION
  Requires: GitHub CLI (gh) authenticated with read access to the repository.
  Output (JSON lines) in reports/mining: pr_comments.jsonl, prs.jsonl, reviews.jsonl
.EXAMPLE   .\Export-PrComments.ps1 -Repo owner/name -Since 2026-01-01
#>
param(
    [string]$Repo,                       # owner/name; default: repository of the current directory
    [string]$Since = ((Get-Date).AddMonths(-6).ToString('yyyy-MM-dd')),
    [int]$MaxPrsForReviews = 300
)
. (Join-Path $PSScriptRoot '_Common.ps1')
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI (gh) not found. Install from https://cli.github.com and run: gh auth login' }
$cfg = Get-FwConfig
$out = Join-Path $script:Root "$($cfg.paths.reports_dir)\mining"
New-Item -ItemType Directory -Force -Path $out | Out-Null
if (-not $Repo) { $Repo = (& gh repo view --json nameWithOwner --jq .nameWithOwner) }
Write-Host "Repository: $Repo  Since: $Since"

# Review comments across all PRs (inline comments + replies)
& gh api "repos/$Repo/pulls/comments?per_page=100&since=${Since}T00:00:00Z&sort=created&direction=asc" --paginate --jq '.[]' |
    Set-Content -Path (Join-Path $out 'pr_comments.jsonl') -Encoding UTF8
# PRs (closed, newest first), keep the merged ones within the window
$prJql = '.[] | select(.merged_at != null and .merged_at >= "' + $Since + '") | {number, title, user: .user.login, created_at, merged_at, html_url}'
& gh api "repos/$Repo/pulls?state=closed&per_page=100&sort=updated&direction=desc" --paginate --jq $prJql |
    Set-Content -Path (Join-Path $out 'prs.jsonl') -Encoding UTF8
# Reviews per PR (one call per PR; capped to protect rate limits)
$prs = Get-Content (Join-Path $out 'prs.jsonl') | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json } | Select-Object -First $MaxPrsForReviews
$revFile = Join-Path $out 'reviews.jsonl'
Set-Content -Path $revFile -Value @() -Encoding UTF8
foreach ($p in $prs) {
    $jq = '.[] | {pr: ' + $p.number + ', user: .user.login, state, submitted_at}'
    & gh api "repos/$Repo/pulls/$($p.number)/reviews?per_page=100" --paginate --jq $jq | Add-Content -Path $revFile -Encoding UTF8
}
Write-Host "Done. Files in $out. Next: extract_comments.py, cluster_comments.py, pr_metrics.py"
Write-Host "Note: output contains reviewer comment text. Keep it inside your organisation; reports/mining is git-ignored."
