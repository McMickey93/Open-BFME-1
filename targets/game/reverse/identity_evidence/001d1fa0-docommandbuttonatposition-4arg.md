# 001D1FA0: Object::doCommandButtonAtPosition, BFME four-argument form

The 417-byte body at RVA 0x001D1FA0 was matched as a naked lift under the Zero
Hour three-argument decoration
?doCommandButtonAtPosition@Object@@QAEXPBVCommandButton@@PBUCoord3D@@W4CommandSourceType@@@Z.
That decoration contradicts the bytes: every exit is `ret 0x10` (four stack
arguments after ECX), and the bool fourth argument at [esp+4+0x40] gates the
voice-response block.

symbols.csv already pins a four-argument decoration (struct-keyed, see below)
?doCommandButtonAtPosition@Object@@QAEXPBVCommandButton@@PBUCoord3D@@W4CommandSourceType@@_N@Z
at ILT 0x00026EF4, which jumps to this body; the AIGroup group caller at
0x00150F40 pushes a false fourth argument.

Shape evidence: the body is the position twin of the matched
Object::doCommandButtonAtObject (0x001D1D10, `..._N@Z`, ObjectDoCommandButtonAtObject.cpp):
the same m_disabled test at +0x1A4, the same PickAndPlayInfo/list<Drawable*>
pickAndPlayUnitVoiceResponse block (here copying *pos into
PickAndPlayInfo::m_position), the same special-power option bits, and the ZH
attack-move (aiAttackMoveToPosition with m_maxShotsToFire) and stop (aiIdle)
cases. The clean C++ in ObjectDoCommandButtonAtPosition.cpp reproduces all 417
bytes plus the trailing jump table.

Class key: `tools/ilt_oracle.py` contradicts the struct-keyed
`...PBUCoord3D@@W4CommandSourceType@@_N@Z` at this body's ILT slot; a sweep of
access, pointer, class-key and trailing-argument variants found exactly one
fit, `...PBVCoord3D@@W4CommandSourceType@@_N@Z`. That agrees with the ledger as
a whole: of the Object/AI rows naming Coord3D that have ILT slots, all 209
struct-keyed (`U`) decorations fall outside their windows while 6 of 12
class-keyed (`V`) ones fit, and the callee
?aiAttackMoveToPosition@AICommandInterface@@QAEXPBVCoord3D@@HW4CommandSourceType@@@Z
is CONFIRMED at 0x00153AF0. BFME declared Coord3D as a class.
