# 0x00BFD210: uw_00bfd210 is the state-0 cleanup funclet of the landed 0x00109EB0 parent

Retail evidence, re-derived from
`inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe`
(image base 0x400000; RVA = VA - 0x400000):

- `0x00BFD210` is 8 bytes: `8b 4d ec` (`mov ecx, dword ptr [ebp-0x14]`) then
  `e9 63 16 05 00` (`jmp 0x0040D828`, the ILT thunk of
  `??1AsciiString@@QAE@XZ`, which itself is `jmp ?releaseBuffer@...`), i.e.
  "destroy the object whose address the saved-esp cookie holds".
- The retail parent `0x00109EB0` (`?bfmeLocalUserMapsReady@@YA_NXZ`, 136 B,
  landed in `game/GameEngine/Source/Common/System/RegistryGetUnsignedIntPublic.cpp`)
  pushes handler stub `0x00BFD1F8` in its EH prologue (`push 0xffd1f8` at
  +0x08). That stub is `mov eax, 0x11EA858; jmp 0x009F6DD6`
  (`___CxxFrameHandler`).
- FuncInfo `0x011EA858` (RVA 0xDEA858) reads `{ magic 0x19930520, count 1, ...
  entry { enclosing -1, action 0x00FFD210 } }`: the parent's unwind map names
  exactly one cleanup action, this funclet. The parent stores EH state 0 at
  +0x42 (`mov dword ptr [esp+0x20], 0`, with esp at the pushed-literal depth)
  before its second by-value `AsciiString` construction call at +0x4A and
  resets it to -1 at +0x4F, so state 0 covers that ctor call: if it throws,
  this funclet destroys the first by-value temporary through the cookie.
- The landed parent now lives in real C++ in
  `game/GameEngine/Source/Common/System/RegistryGetUnsignedIntPublic.cpp`;
  that TU's EH COMDAT emits the funclet as object label `$L3599`
  (section 23, value 0; `__ehhandler$?bfmeLocalUserMapsReady@@YA_NXZ` at +8)
  with exactly the 8 retail bytes above.

The generated placeholder `uw_00bfd210` (`game/gen_small/uw_gen_013.cpp`,
object-symbol `$L7849`) kept the bytes while the parent was a byte dump.
With the parent landed as real C++, that TU emits the funclet itself, so the
generated copy would duplicate the address. The row must move to the parent's
TU with the real object label; the extent (8 B) and the retail address are
unchanged and were never wrong.
