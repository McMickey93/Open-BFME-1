# Integer-list append COMDAT ownership

## Target evidence

At verified BFME 1 base 39e371392398a33a30e1a6b3af67e5662a745bb1,
Team_DoXfer.cpp and ScriptEngine/XferListInt.cpp inline the integer-list append
but also emit competing out-of-line list<int>::push_back definitions.
The vendored STLport _list.h defines push_back(value) as insert(end(), value).

A file-static inline appendListWord adapter invokes exactly that operation.
Both complete consumers retain their byte-exact rows and stop defining
?push_back@?$list@HV?$allocator@H@_STL@@@_STL@@QAEXABH@Z.
The retail-proven 45-byte provider at RVA 0x000E66B0 in
ShellMenuSchemeManager_parseImagePart_Thunk.cpp remains unchanged, including
its opaque ?dup_000e66b0@@YAXXZ row and existing alias notes.
The integer-list pin still routes through ILT 0x0001E00B to that body.
This repair does not promote the physical body's disputed identity.

## Native verification

The completed local native MSVC 7.1 checks passed all 94 consumer/provider
rows and eight DIR32 references, with no baselined body-guard failure.
The declared-body and ledger checks passed. Object-symbol inspection found
the competing definition in both original consumers and in neither edited
consumer. The donor gitlink has zero affected build dependencies.
The completion workflow repeats the normal builds and commit/push hooks.

Before and after linked previews were UNKNOWN because
build/link_census/link_index.pkl was unavailable. The queue's 843+267=1,110
bytes are a ranking estimate; they are not measured linked progress.
There are +0 newly exact C++ bytes and +0 newly covered bytes.

## Controls and donor provenance

Extern-template suppression prevents required caller inlining. Imported or
specialized member wrappers change child outlining or register saves;
flattened member forms also alter code generation. Those trials were reverted.
The successful adapter has no dllimport, type pun, shared-header change,
new address pin or runtime helper.

BFME 2 donor snapshot: 09babd75f455d94ec1cd253fdc06c32d94184d6f.
Reviewed donor: Code/Libraries/Source/WWVegas/WWLib/stlport_list_int_o1.cpp.
Its file-static _Construct overload demonstrates localizing template work to
avoid an unwanted external COMDAT. The particular BFME 1 append repair is a
local adaptation, not a transfer of donor ABI, allocator flags or addresses.
A bounded donor scan of stlport_narrow_num_put.cpp found 10 bodies and 2,414
placements: 37 near and 2,377 exact-multi; no exact-unique recovery.
This was not an exhaustive scan of every reference lane.

Autonomous implementation and measurements: OpenAI Codex.
