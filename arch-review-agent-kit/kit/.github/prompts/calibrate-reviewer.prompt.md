---
description: Back-test the reviewer against historical architect comments (recall/precision report)
agent: review-calibrator
---
Back-test the reviewer on these PRs: ${input:prs:PR numbers, or "newest 10 mined PRs"}.
Run blind, compare with the architect's actual comments, and write the calibration report with missed comments, noisy rules and scoring suggestions.
