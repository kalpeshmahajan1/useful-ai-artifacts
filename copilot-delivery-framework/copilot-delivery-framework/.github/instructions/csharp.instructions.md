---
applyTo: "**/*.cs"
---
# C# rules (.NET Framework 4.8, C# 7.3)
Compile target is C# 7.3. Check csproj/packages.config before using any API. Match the module's existing patterns for logging, DI and data access.
<!-- GENERATED:RULES scope=csharp -->
- [CS-001] (blocker) Use only C# 7.3 syntax (no switch expressions, ??=, using declarations, ranges, records, init, nullable annotations, file-scoped namespaces).
- [CS-006] (blocker) Build SQL only with parameters (or the project's data layer); never concatenate or interpolate values into SQL text.
- [CS-002] (major) Use only APIs available on .NET Framework 4.8 or in packages already referenced by the project; do not add packages without an ADR.
- [CS-003] (major) Do not block on Tasks (.Result, .Wait(), .GetAwaiter().GetResult()) in request or UI paths; await instead.
- [CS-004] (major) Async methods return Task; async void only for event handlers.
- [CS-005] (major) Never use an empty catch; handle, log with context, or rethrow.
- [CS-007] (major) Wrap IDisposable resources you create in using blocks (C# 7.3 form) or dispose them in the owner's Dispose.
- [CS-008] (major) Classes have one reason to change; depend on abstractions at layer boundaries; no new static state or service locators.
<!-- /GENERATED -->
