---
applyTo: "**/*.cs"
description: "C# 7.3 / .NET Framework 4.8 coding rules"
---
# C# (7.3) on .NET Framework 4.8

## Language limits (hard)
- C# 7.3 only. **Do not use:** nullable reference types (`string?`), switch expressions, `record`, `init`, `using var` declarations, ranges/indices (`^1`, `..`), async streams, default interface methods, static local functions, `??=`, pattern-matching beyond what 7.3 supports (`is Type t`, `switch` with `case Type t when` are OK).
- .NET Framework 4.8 APIs only. No `System.Text.Json` / `IHttpClientFactory` / `Span` features unless the project already references the package.

## Style: copy the neighbours
- Match the sibling files for namespaces, regions, naming (`_camelCase` fields vs other), brace style, `var` usage, XML docs, DI style, logging calls, exception types. If unsure, open the nearest similar class and mirror it.
- Follow `.editorconfig` and any StyleCop/analyzer rulesets present.

## Simplicity and OOP/SOLID
- Methods do one thing; prefer early return over deep nesting; keep cognitive complexity low (Sonar S3776).
- Single Responsibility: no god classes/methods; business logic does not live in controllers, Windows service hosts or UI code-behind.
- Introduce an interface/abstraction only where the codebase already has that seam (DI/testing). No speculative generics, no deep inheritance, no pattern for pattern's sake.
- Composition over inheritance; depend on abstractions at layer boundaries; no service locator unless already standard.
- Explicit over clever: avoid dense LINQ chains and one-liners that hide control flow.

## Correctness and safety
- ASP.NET (non-Core) has a synchronization context: **never block on async** (`.Result`, `.Wait()`); use `async/await` end-to-end, `ConfigureAwait(false)` in library code if the codebase does.
- Dispose `IDisposable` (`using { }` block form). Reuse `HttpClient`; do not new it per call.
- Throw specific exceptions; never swallow; never `catch (Exception)` without logging and a reason; preserve stack (`throw;`).
- Parameterized SQL only. Validate inputs at boundaries.
- **PHI:** never log patient name/ID/DOB/accession/UIDs-with-patient-context; follow existing audit conventions.
- Hot imaging paths: avoid needless copies/allocations of pixel buffers; otherwise do not micro-optimize.

## Tests
New logic gets unit tests in the existing test framework/style (naming, arrange-act-assert, mocking library already in use).

Learned architect rules for C#: see `learned-csharp.instructions.md`.
