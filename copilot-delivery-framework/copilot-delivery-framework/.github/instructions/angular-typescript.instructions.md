---
applyTo: "**/*.ts,**/*.html"
---
# Angular 21 / TypeScript rules
Follow the module's existing component, service, state and HTTP patterns before introducing anything new.
<!-- GENERATED:RULES scope=typescript -->
- [NG-002] (major) Every RxJS subscription must be torn down (async pipe, takeUntilDestroyed/takeUntil, or unsubscribe).
- [NG-003] (major) Do not bypass Angular sanitization or bind unsanitized HTML; patient/user-controlled text must never be rendered as HTML.
- [NG-005] (major) Use the project's existing HTTP/state/UI patterns and libraries; adding a new library needs an ADR.
- [NG-001] (minor) Do not use 'any'; use a specific type or unknown with narrowing.
- [NG-004] (minor) Components bind and delegate; business logic and data access belong in injectable services.
<!-- /GENERATED -->
