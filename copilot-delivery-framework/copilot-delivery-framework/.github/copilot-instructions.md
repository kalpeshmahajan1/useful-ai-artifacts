# Repository instructions (keep this file under ~3,800 characters: code review reads only the first ~4,000)

Product: enterprise medical imaging viewer. Correctness and traceability outweigh speed and cleverness.
Stack: ASP.NET on .NET Framework 4.8, C# 7.3, Angular 21 + TypeScript, JavaScript (prototype/OOP style), SQL Server, C++.

## Always
- Smallest change that meets the requirement. No speculative abstractions, layers, patterns or packages.
- Follow the surrounding code and `design/DESIGN-CONSTRAINTS.md`. If a request conflicts with them, say so and stop.
- Before coding, read the rules for the file type in `guidelines/rules/`. Cite rule IDs (e.g. CS-005) in reviews.
- Never invent APIs, packages, files or test results. If unsure, say "unverified" and name what to check.
- Never put patient data in code, logs, tests or examples. Synthetic data only.
- Changes under `critical_paths` (framework.config.json) need human architect sign-off; say so explicitly.

## Review output
Per finding: file, lines, exact code, issue, rule ID, severity (blocker/major/minor/nit), confidence (certain/likely/verify), fix, acceptable-if-unfixed. Do not report anything without a rule or a concrete defect with evidence in the shown code.

## Active rules (generated; edit guidelines/rules/*.md then run scripts/python/compile_instructions.py)
<!-- GENERATED:RULES scope=all,design,process -->
- [GEN-003] (blocker) Never commit credentials, tokens, keys or connection strings with passwords; use the project's secure configuration.
- [HC-001] (blocker) Never write patient-identifying data (name, ID, birth date, accession, UIDs linked to a person) to logs, exceptions, URLs or telemetry.
- [DES-001] (major) Respect layers and allowed dependencies defined in design/DESIGN-CONSTRAINTS.md.
- [DES-002] (major) Do not change wire formats or public contracts (DICOM, HL7, FHIR, WADO-RS, REST) without an ADR and a compatibility check.
- [GEN-001] (major) Make the smallest change that meets the requirement; no speculative abstraction, new layers or new dependencies.
- [HC-002] (major) Changes in files listed under critical_paths need explicit human architect sign-off and a test or documented verification.
- [HC-003] (major) In clinical data paths, never fall back silently to defaults or partial data; surface an error state the user can see.
- [GEN-002] (minor) Follow the naming, structure and patterns of the surrounding module; do not reformat or refactor untouched code in a feature change.
- [GEN-004] (nit) TODO/FIXME/HACK comments must reference a work item.
<!-- /GENERATED -->
