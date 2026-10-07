# Solution design philosophy

> Living document. Seeded from stated goals; **fill the TODO sections** (or let `/learn-from-prs` propose entries as CONTEXT-NOTEs for you to approve).

## Guiding principles
1. **Simplicity over cleverness.** Readable beats fancy. A junior dev should follow the code on first read.
2. **Consistency over personal preference.** Follow what the codebase already does, even if you would do it differently.
3. **SOLID and OOP applied pragmatically.** Use them to remove real pain (coupling, untestable code, god classes), not to add layers "just in case".
4. **No speculative generality.** No interfaces with one implementation unless the codebase already does so for that layer (for DI/testing seams); no config knobs nobody asked for.
5. **Small, cohesive classes and methods.** One reason to change.
6. **Fail loudly, log safely.** Specific exceptions, no swallowed errors, no PHI in logs.
7. **Performance matters in imaging paths** (pixel data, large series, streaming). Avoid needless allocations/copies on hot paths; do not micro-optimize elsewhere.

## Architecture map (TODO - fill)
- Layers and allowed dependency direction: TODO
- Where business logic lives vs controllers/services/repositories: TODO
- DI/composition approach (e.g. Unity/Autofac/manual): TODO
- Data access approach (ADO.NET/EF/Dapper, stored procs vs inline SQL): TODO
- Native (C++) interop boundary rules: TODO
- Frontend: module/standalone convention, state management, API-client pattern, signals vs RxJS convention: TODO
- Configuration & deployment (web.config transforms, IIS, Windows services): TODO

## Domain notes (TODO - fill / grows via curator)
- DICOM/PACS/VNA conventions (tag handling, transfer syntaxes, WADO-RS, FHIR mapping, UID handling): TODO
- PHI handling and audit requirements: TODO
- Threading/async rules under ASP.NET 4.8 (sync context, `ConfigureAwait`, blocking calls): TODO

## Explicit anti-patterns for this product
- Over-engineered abstractions, deep inheritance, generic repositories wrapping already-simple code
- Clever LINQ/one-liners that hide control flow
- New NuGet/npm packages for trivial needs
- Static mutable state, service locators, hidden singletons (unless the codebase already standardizes them)
- Business logic in controllers, components, or SQL triggers (TODO confirm)
