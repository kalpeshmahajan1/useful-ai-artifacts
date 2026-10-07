---
applyTo: "**/*.js"
---
# JavaScript (prototype / OOP) rules
Code uses constructor functions and prototypes. Preserve the existing inheritance style; do not convert to classes or modules unless asked.
<!-- GENERATED:RULES scope=javascript -->
- [JS-001] (major) Do not assign an object literal to X.prototype without restoring 'constructor'; prefer adding methods individually.
- [JS-002] (major) Never add members to built-in prototypes (Array, Object, String...).
- [JS-004] (major) Never use eval, new Function or string arguments to setTimeout/setInterval.
- [JS-005] (major) Do not assign HTML strings (innerHTML, document.write) built from data; use textContent or DOM APIs.
- [JS-003] (minor) Use === and !== instead of == and !=.
- [JS-006] (minor) In constructor functions, define methods on the prototype rather than per instance, unless closure privacy is required.
<!-- /GENERATED -->
