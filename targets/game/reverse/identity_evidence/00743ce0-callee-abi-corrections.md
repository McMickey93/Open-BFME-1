# 0x00743CE0 callee ABI corrections (BFME 1 target evidence only)

Converting W3DView 0x00743CE0 (530 B, vtable 0x011217A0 slot 115) exposed two
callee rows whose names had the right bytes but the wrong ABI. Both stay
address-derived; only the signatures change.

## 0x0073A680 (33 B) returns its out parameter

- Body: `mov edx,[ecx+4B8]; mov eax,[esp+4]; mov [eax],edx; ... ; ret 4`.
  EAX holds the out pointer at the return.
- Caller 0x00743CE0 +0x135..+0x152: `lea edx,[esp+0C]; push edx; call ILT
  0x16F4; mov edx,[eax]; ... mov [ecx],edx` copies the vector through the
  returned EAX, so the callee returns the pointer it was given.
- Old spelling `?getPosition@Rva0073A680@@QBEXPAUVec3@@@Z` (void) cannot
  produce that caller; new spelling
  `?getPosition@Rva0073A680@@QBEPAUVec3@@PAU2@@Z`, same 33 bytes.

## 0x005A4570 (59 B) is a Mouse member

- Both call sites in 0x00743CE0 (+0x1E4 and +0x1FE) load
  `mov ecx,[0x012F4C5C]` (TheMouse) immediately before `call ILT 0x406DD`,
  and nothing else is computed into ECX: a thiscall on TheMouse.
- The body never reads ECX; it re-reads TheTacticalView and TheMouse, which is
  how a member that names the global instead of `this` compiles.
- Old spelling `?bfmeGo1083B@@YAXXZ` (free function) cannot produce the ECX
  loads; new spelling `?rva005A4570@Mouse@@QAEXXZ`, same 59 bytes. No source
  file called the old name.
