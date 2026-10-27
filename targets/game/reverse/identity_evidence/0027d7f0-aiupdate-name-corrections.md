# AIUpdate.cpp name corrections with 0x0027D7F0 (BFME 1 target evidence)

- `AI_MOVE_OUT_OF_THE_WAY -> BFME_AI_MOVE_OUT_OF_THE_WAY`: the reference enum
  value is 0x17, but retail privateMoveAwayFromUnit (0x0027D7F0) compares the
  temporary state with 0x1A (`cmp dword ptr [eax+4],0x1a` at +0xAA) and pushes
  0x1A to the temporary-state setter at +0x1EF. The ZH enumerator is kept for
  the ZH code paths; this body uses the BFME number, named like the TU's
  existing BFME_AI_FOLLOW_WAYPOINT_* constants.
- `g_rva01075350 -> BfmeBoundaryZero3D`: same VA 0x01075350 (a 0.0f .rdata
  float); dir32_addresses.csv records `?BfmeBoundaryZero3D@@3MB` there and the
  live DIR32 check refuses the unrecorded spelling for needToRotate's operand.
  Bytes are unchanged; only the recorded name is used.
