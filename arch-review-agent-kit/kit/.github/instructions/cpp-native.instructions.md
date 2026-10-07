---
applyTo: "**/*.cpp,**/*.h,**/*.hpp,**/*.c"
description: "C++ native / interop conventions"
---
# C++ (native imaging code)

- Match the project's existing C++ standard level, naming, header layout and error-handling style.
- RAII for every resource; no raw owning pointers; no manual `new/delete` where a smart pointer or container fits the existing style.
- Check bounds and sizes on all buffer operations (pixel data!); validate inputs at the interop boundary; const-correctness.
- Keep the managed/native boundary narrow and explicit (marshalling, ownership, who frees what). Document ownership in comments.
- No exceptions crossing the native boundary unless the existing design does.
- Simplicity first: no template metaprogramming or clever macros.

Learned architect rules: `learned-cpp.instructions.md`.
