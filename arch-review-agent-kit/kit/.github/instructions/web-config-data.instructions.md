---
applyTo: "**/*.js,**/*.xml,**/*.json,**/*.config,**/*.xaml"
description: "JavaScript, XML, JSON, config conventions"
---
# JavaScript / XML / JSON / config

- Match existing formatting, key naming and ordering. Do not reformat whole files.
- JSON: valid, no comments unless the file type allows, consistent casing with siblings.
- `web.config` / `app.config`: no secrets or connection strings with credentials in source; use transforms/secure config the project already uses. IIS-specific settings (timeouts, request limits, compression) change only with justification.
- XML/XAML: follow existing namespace prefixes and element ordering.
- Plain JavaScript (non-TS): `const/let`, strict equality, no globals, no `eval`.
- `package.json`/lock files: do not add dependencies for trivial needs; never hand-edit lock files.

Learned architect rules: `learned-config-js.instructions.md`.
