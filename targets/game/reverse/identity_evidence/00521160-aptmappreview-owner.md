# RVA 0x00521160 belongs to AptMapPreview; method spelling remains unknown

Retail-1.03-unpacked lotrbfme.exe (base 0x00400000), decoded with pefile and
capstone, proves an AptMapPreview receiver and MapMetaData* argument.
This is owner/ABI evidence only, not a proof of an authentic method name.

## Receiver chain from matched BFME code

The clean matched AptMapPreview::rva005216B0(MapMetaData*) (80 bytes,
GUI/AptMapPreview.cpp) saves its incoming ECX into ESI at RVA 0x005216B8.
At 0x005216DB it pushes the original metadata argument, restores ECX=ESI,
and calls ILT 0x0001A870 at 0x005216DE. That E9 reaches 0x00521390.

The 591-byte intermediate body saves its incoming ECX into ESI at
0x005213AC. Its common non-null-window tail at 0x005215BF loads the unchanged
argument from [ESP+28h], pushes it, restores ECX=ESI at 0x005215C4 and calls
ILT 0x00016239 at 0x005215C6. That E9 reaches the target 0x00521160.
This is an ordinary CALL, not a tail jump. The null-window early exit omits
this update. No constructor or secondary-subobject adjustment intervenes.

The class identity is independently supported by matched mapGadgetInit
0x00521990 and initGadgets 0x00521AE0, with BFME registration strings
AptMapPreview::MapGadgetInit and AptMapPreview::Picture. The matched
constructor 0x00520670 writes its windows at +4/+8/+C/+10, zeros eight child
window pointers at +0x14 through +0x30, and allocates MapMetaData at +0x3C.
The target accesses exactly those fields; this is not an owner guessed from
nearby addresses or the Zero Hour source tree.

## Target ABI, data and extent

The target saves ECX as EDI at 0x00521184 and loads its single stack argument
into ESI at 0x0052117B. It reads metadata player count at +0x20, multiplayer
byte at +0x24 and position-name table at +0x38. Its Player_%d_Start formatting
and GUI:Blank localization update the child windows at receiver +0x14.
It compares metadata to the constructor's receiver +0x3C and hides or clears
unused windows up to eight. The body has an SEH string lifetime and two
RET 4 paths. The final RET 4 starts at 0x0052131C and ends at 0x0052131F;
INT3 starts at 0x0052131F, proving 447 bytes from 0x00521160.

The old blocked records' claim that no checked owner layout or named caller
exists is superseded by this chain. The name of the operation is still
unproven: component behavior alone cannot establish an EA C++ spelling.
An eventual reconstruction can use an address-preserving AptMapPreview
member and the observed MapMetaData* ABI. No source reconstruction, ledger
rename, pin or data change is made in this evidence-only session.

## Clean C++ donor recovery

BFME 2's GameClient/GUI/GUICallbacks/Apt/AptMapPreview.cpp contains the clean
UpdateMapStartSpots body at RVA 0x0057DA21 (374 bytes). Its WorldBuilder-backed
method spelling is not asserted for BFME 1: the new member remains
AptMapPreview::rva00521160(MapMetaData*). The donor supplies the two map/default
branches, waypoint lookup, eight child-window loop, and GUI:Blank fetches.
BFME 1 checks m_isMultiplayer on each iteration and has no GameLogic mode gate.
The existing BFME constructor and caller chain above establish the layouts.

The waypoint map is at metadata+0x38. The existing typed _M_find pin at ILT
0x00010AAF uses map<AsciiString, Coord3D>; node payload +0x14 is passed to
positionStartSpotControls. That matched helper's native declaration uses
GameWindow *buttonMapStartPositions[] as its last argument. The source retains
that array declaration rather than introducing a different mangled ** contract.
The observed bool at preview+0x39 is the winEnable input. TheGameText fetch
uses virtual slot +0x28 and returns the canonical UnicodeString by value.

A complete donor port initially emitted 450 bytes with the receiver in EBP
instead of EDI and the waypoint tree in EDI instead of EBP. A named
Coord3D *position = &it->second before the five-argument positioning call
settles both register allocation and the metadata-push ordering. It emits all
447 target bytes with 25 aligned relocation slots. Four other local/loop
spellings were inert; eight EH combinations did not improve the initial form.

The strict scoped build verifies all seven TU rows, nine literals plus one
empty-string reference, all five DIR32 references, and body guards. The
pre-existing cleanup's compiler label was repinned solely by eh_state_pins.py
against its retail parent's unwind state. link_check.py before/after reports
LINKED 0 -> 0 bytes: no existing linked bytes are lost. No pin, header, shim,
assembly, or hatch was introduced.
