# ScriptEngine::setSequentialTimer(Team *, Int) at 0x003399D0

The 52-byte body at 0x003399D0 was ledgered as the placeholder
`?bfmeAssign@Gen_003399D0@@QAEXPAXH@Z` (Bfme5SixtyEight.cpp).

- Its ILT 0x00010DC5 is pinned in symbols.csv as
  `?setSequentialTimer@ScriptEngine@@QAEXPAVTeam@@H@Z`. Retail .text reaches
  that ILT from 0x002F50AE and 0x002F50C7 (inside the matched
  `ScriptActions::doTeamIdleForFramecount` 0x002F5040, which declares and
  calls this name), 0x002F54A0 (tail jump) and 0x00302D2B.
- `ilt_oracle.py check ?setSequentialTimer@ScriptEngine@@QAEXPAVTeam@@H@Z
  0x003399D0` reports CONFIRMED (exact).
- The body is Zero Hour's Team overload: return on a null team, walk
  m_sequentialScripts (+0x0C/+0x10, the same vector the matched Object
  overload at 0x00339980 walks), set m_framesToWait (+0x20) on the first
  script whose m_teamToExecOn (+0x04) is the team.
- It sits right after the Object overload (0x00339980, 55 B), the same
  pairing as Open-BFME-2's matched rows 0x00203FCF (Object) and 0x00204002
  (Team, 48 B) in ScriptEngine_setSequentialTimer.cpp.
