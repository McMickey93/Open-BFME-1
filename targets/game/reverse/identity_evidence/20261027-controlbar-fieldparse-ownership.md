# ControlBar FieldParse storage identity

Target: `game/GameEngine/Source/GameClient/GUI/ControlBar/ControlBarSchemeManagerBodies.cpp`.
The whole unit owns the already matched image parser at RVA 0x004AE920 (172 B)
and animation parser at RVA 0x004AEA00 (219 B).

The BFME 1 address record owns the image table at VA 0x010FD030 as
`?g_controlBarSchemeImageFieldParse@@3QBEB`, and the animation table at
VA 0x010FD0A8 as `?g_controlBarSchemeAnimationFieldParse@@3QBEB`.
The old extern declarations instead emitted `@@3QBUFieldParse@@B` references.
Declare the existing byte-storage names and apply the `const FieldParse *`
view only when passing each address to INI::initFromINI. This establishes no
new table extent, data definition, pin, alias or class layout.

Native MSVC 7.1 verification with the TU's unchanged flags passes both rows
before and after the change, including both DIR32 sites. The original build
was already byte-exact; this repair aligns its external COFF names with the
recorded owners. The rebuilt object contains both canonical `@@3QBEB` names
and neither former typed-array name.

Each exception was removed by its own unmodified `tools/repair_queue.py
pass-test` invocation. Both completed with 2/2 functions and both DIR32
references verified. The declared-body check also passes. The source comments
retain the former decorated references as provenance and let the supported
pass-test locate the complete affected unit, following the existing
PlayerListConstructorClean.cpp retired-debt pattern.

Donor freshness: reviewed BFME 2 09babd75f455d94ec1cd253fdc06c32d94184d6f
against official 73898a96342963eac2826836db10649a69e3dbb8. The reviewed
`Code/GameEngine/Source/GameClient/GUI/ControlBar/ControlBarScheme_ControlBarSchemeManager_newControlBarScheme.cpp`
is unchanged. Its INI callbacks are context, not proof of BFME 1 addresses or
layout. No BFME 2 code or build headers were imported; this TU includes only
its existing BFME 1 STLport inputs. No donor compile-trial cache existed to
refresh. The updated reference is a discovery reference, not a build input.

Result: two keyed DIR32 exceptions retired; +0 new exact C++ bytes. No linked
byte gain or whole-game/runtime success is claimed without a current census.

Autonomous implementation and verification: OpenAI Codex.
