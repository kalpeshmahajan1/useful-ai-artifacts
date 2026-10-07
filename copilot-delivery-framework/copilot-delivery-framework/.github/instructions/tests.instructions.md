---
applyTo: "**/*Tests?.cs,**/*.spec.ts,**/*.test.ts"
---
# Test rules
Synthetic data only. Tests must be deterministic.
<!-- GENERATED:RULES scope=tests -->
- [TST-001] (major) A bug fix includes a test that fails without the fix, or the PR states why a test is not possible.
- [TST-002] (minor) Tests must not depend on wall-clock time, sleeps, network or machine state; use synthetic data only.
<!-- /GENERATED -->
