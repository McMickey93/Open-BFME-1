# Queue 6: ICoord2D vector resize

The October 19 census e9a5ae5b4c contains a retail copy in
`game/Libraries/Source/WWVegas/WWLib/vector_ICoord2D_resize.cpp` and wrong
copies in MapUtil, WorldHeightMap, and immutable `game/gen_small/zhstl_005.cpp`.
The retail body at RVA 0x00453DF0 takes an uninitialized default element;
the wrong copies zero-initialize it. The queue's parser/thunk files are consumers.

A TU-local specialization declaration removes the incorrect WorldHeightMap
emission while leaving its callers bound to the independently matched owner.

The same change in MapUtil was attempted and reverted: the scoped 203-row check
failed 59 rows, mostly because resize was the only reason MapUtil emitted
ledger-backed copy/fill/erase helpers and their many aliases. MapUtil cannot be
repaired by a declaration alone: its required helper instantiations must remain.
The check also reported preexisting less<AsciiString> callee-address disagreement;
no pin or baseline was changed to hide it.

`link_check.py Rva0000366BICoord2DVectorResizeThunk.cpp` before the repair reported
selected resize not retail, and selection UNKNOWN because the copied census
cannot prove 22,634 current objects. Inspecting the newly compiled WorldHeightMap
COFF confirms the resize definition is absent. This is partial emitter cleanup;
MapUtil and the generated emitter still prevent a complete LINKED claim.

Final source check: `./build.sh game/GameEngineDevice/Source/W3DDevice/GameClient/WorldHeightMap.cpp`
passes 127/127 functions, 12 data rows, 12 float constants and 104 DIR32
references. Existing two funclet labels were rediscovered by bytes.
