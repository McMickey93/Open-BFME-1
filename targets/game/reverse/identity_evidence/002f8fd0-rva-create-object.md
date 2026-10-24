# 0x002F8FD0 is the BFME counterpart of ScriptActions::doCreateObject (address-derived name)

The row was `?d_002f8fd0@@YAXXZ`, a 563 B `__emit` lift. Its old
doMoveCameraAlongWaypointPath name was refuted and tombstoned (re_attempts,
"object creation body").

## Evidence

1. Callers. Only ILT 0x0003D3CA jumps to the body. Its only two calls are at
   0x003052F8 and 0x0030ADC4, both inside the matched
   `?executeAction@ScriptActions@@UAEXPAVScriptAction@@@Z` (0x00303BF0).
   Zero Hour's ScriptActions::executeAction calls doCreateObject from exactly
   two cases.
2. ABI. The body is `__thiscall` and ends in `ret 0x14`: five stack words,
   which fits three `const AsciiString &`, one `Coord3D *` and a `Real`.
3. Literals. It uses "WARNING - Object with name ",
   " already exists. Failed Create." and "***WARNING - Team not found:***".
   Those are the strings of Zero Hour's doCreateObject.
4. Behaviour. Its flow is Zero Hour's doCreateObject: the unnamed-unit compare
   at this+0x0C, the getUnitNamed/dead test, the team lookup, findTemplate and
   newObject, the name transfer or cache, then setOrientation(angle) and
   setPosition(pos).
   BFME drops the createTeam fallback and the crater branch. The matched
   sibling createUnitOnTeamAt (same TU) shows the same BFME call shapes.
5. Bytes. The C++ in ScriptActions.cpp compiles to retail's 563 bytes exactly
   (tools/probe.py EXACT).

## Why the name stays address-derived

`tools/ilt_oracle.py check` reports CONTRADICTED for
`?doCreateObject@ScriptActions@@IAEXABVAsciiString@@00PAUCoord3D@@M@Z` at this
body, p_false=1.7e-3. ILT slot 49345 needs a name hashing into buckets
29243-29268.

A search of about 26,000 spellings fits only at chance level. It varied
access, const, by-value or pointer arguments, the Real/Int/Bool angle, 24
method names and 3 classes. So BFME's real decorated name is unknown. The
row lands as `?createObject@Rva002F8FD0ScriptActions@@QAEXABVAsciiString@@00PAUCoord3D@@M@Z`.
The evidence above says what the body does, not what it was called.
