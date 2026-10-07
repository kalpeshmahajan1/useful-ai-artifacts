---
applyTo: "**/*.ts,**/*.html,**/*.scss,**/*.css"
description: "Angular 21 / TypeScript conventions"
---
# Angular 21 / TypeScript

- **First rule: mirror the existing frontend code** (component structure, folder layout, state approach, API-service pattern, naming, template style). Use modern Angular features (standalone components, signals, `@if/@for` control flow, `inject()`) **only to the extent the codebase already does**; do not migrate styles opportunistically.
- Strict TypeScript: no `any` (use proper types/`unknown`), no non-null `!` without justification, explicit return types on public methods.
- Components stay thin: UI + binding only; logic in services; no HTTP in components; no business rules in templates.
- RxJS: always unsubscribe/complete (async pipe, `takeUntilDestroyed`, or the codebase's pattern); no nested subscribes; keep operators readable.
- Change detection: follow the project default; avoid heavy work in template expressions/getters.
- Imaging UI: avoid per-frame allocations, avoid layout thrash in render loops, keep canvas/WebGL resource cleanup in destroy hooks.
- Never log PHI to the console; never put PHI in URLs or local storage unless an existing approved pattern does so.
- Accessibility basics for new UI (labels, keyboard, roles) consistent with existing screens.
- Tests: follow the existing runner/style; test behavior, not implementation details.

Learned architect rules: `learned-angular-typescript.instructions.md`.
