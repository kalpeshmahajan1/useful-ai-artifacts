---
applyTo: "**/*.sql"
---
# SQL rules
Scripts must be re-runnable and backward compatible.
<!-- GENERATED:RULES scope=sql -->
- [SQL-002] (major) Schema changes ship as versioned, re-runnable, backward-compatible scripts with a rollback note.
- [SQL-001] (minor) List required columns instead of SELECT * in application queries.
<!-- /GENERATED -->
