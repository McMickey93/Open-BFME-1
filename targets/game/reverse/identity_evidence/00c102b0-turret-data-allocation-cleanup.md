# Turret-data allocation cleanup at RVA 00C102B0

The matched AIUpdateModuleData::parseTurret body at 0026E7D0 pushes handler
00C102BB. The handler loads FuncInfo 00DFF498. Its sole unwind entry maps
state 0 to -1 through action 00C102B0, independently establishing ownership.
The action reads the allocation from EBP+0C, calls the established global
operator delete at 00881EB0, pops the argument and returns at 00C102BA.
These instructions establish the complete 11-byte extent.

Global allocation in the native parser emits the corresponding single-state
map and action $L96839. The prior placement expression emitted an extra pool
tag and selected class placement delete. Replacing it with global new fixes
the failure action while preserving every byte of the 146-byte parent.
No shared-header change, additional pin or assembly is needed.

The scoped AIUpdate.cpp gate passes all 62 recorded bodies and checks its
25 string literals, three float constants and 82 DIR32 references. This is
the only open dump reached by the file's native parent unwind maps. The
cleanup name retains its address rather than asserting an original name.
