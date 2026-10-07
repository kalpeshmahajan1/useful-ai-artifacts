---
applyTo: "**/*.sql"
description: "SQL Server / T-SQL conventions"
---
# SQL Server (T-SQL)

- Match existing naming, schema usage, script header and idempotency conventions (look at neighbouring migration/scripts).
- Parameterized queries only; no string-concatenated SQL. Explicit column lists; no `SELECT *`.
- Set-based over cursors/loops unless justified. Avoid scalar UDFs and implicit conversions on indexed columns in hot queries.
- Scripts must be re-runnable (`IF NOT EXISTS`) if existing scripts are.
- Consider indexes and locking impact for large imaging tables (studies/series/instances); note the expected cardinality.
- No PHI in sample data or comments.

Learned architect rules: `learned-sql.instructions.md`.
