# Design constraints (maintained by architects)

> The framework cannot know your architecture. Every `<<FILL>>` below must be completed by an architect
> before the reviewer and design-guardian agents can enforce anything in that section. Keep it short and
> checkable: a statement an engineer can verify by reading a diff. Anything unverifiable does not belong here.
> Reference ADRs in `design/decisions/` instead of repeating rationale.

## 1. Platform and language ceiling
- .NET Framework 4.8, C# 7.3, SQL Server, Angular 21 / TypeScript, JavaScript (prototype style), C++ (native imaging components).
- Language level and target framework are changed only by ADR.

## 2. Layers and allowed dependencies
<<FILL: list layers top to bottom, e.g. Presentation -> Application services -> Domain -> Data access -> Infrastructure.
State for each layer what it may reference and what it must never reference. Mirror the forbidden ones in design/forbidden-patterns.json.>>

## 3. Data access
<<FILL: the single approved way to reach the database (repository/ORM/stored procedures), transaction rules, who owns connections.>>

## 4. External contracts and standards
<<FILL: DICOM / HL7 / FHIR R4 / WADO-RS / XDS / REST contracts the product exposes or consumes; where conformance statements live; versioning/compatibility policy for public endpoints and messages.>>

## 5. Threading, async and long-running work
<<FILL: ASP.NET request-path rules, background services/Windows services, UI thread rules, cancellation conventions.>>

## 6. Error handling, logging and diagnostics
<<FILL: exception strategy per layer, logging framework and levels, correlation ids, what must never be logged (patient-identifying data).>>

## 7. Configuration, security and deployment
<<FILL: configuration sources, secret handling, authN/authZ approach, IIS/Windows Server/Azure VM deployment assumptions that code may rely on.>>

## 8. Frontend
<<FILL: module structure, state management, HTTP access pattern, component conventions, approved libraries, how legacy prototype-based JavaScript and Angular coexist.>>

## 9. Native (C++) and interop
<<FILL: ownership and memory rules at the managed/native boundary, approved marshalling patterns, build toolchain constraints.>>

## 10. Critical paths (human sign-off required)
<<FILL: describe code areas where a defect can change what a clinician sees or decides. Put the matching globs in framework.config.json -> critical_paths.>>

## 11. Explicit non-goals (what we deliberately do NOT do)
<<FILL: patterns, frameworks or abstractions the team has decided against, so agents stop proposing them.>>
