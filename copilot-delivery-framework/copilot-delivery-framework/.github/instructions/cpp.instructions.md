---
applyTo: "**/*.cpp,**/*.h,**/*.hpp,**/*.cc"
---
# C++ rules
State ownership of every buffer, especially at managed/native boundaries.
<!-- GENERATED:RULES scope=cpp -->
- [CPP-001] (major) Do not use gets/strcpy/strcat/sprintf/vsprintf; use bounded or std:: alternatives.
- [CPP-002] (major) Own resources with RAII types (std::unique_ptr, std::vector, handles wrappers); no owning raw pointers or manual delete.
- [CPP-003] (major) At C++/.NET boundaries, state who allocates and frees every buffer and how strings/arrays are marshalled.
<!-- /GENERATED -->
