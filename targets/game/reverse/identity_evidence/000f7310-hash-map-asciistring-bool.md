# _STL::hash_map<AsciiString,bool,rts::hash<AsciiString>,rts::equal_to<AsciiString>>::operator[]

Retail 0x000F7310 (142 bytes) is a hash_map<AsciiString, T>::operator[]
insertion body whose mapped type T is one byte (byte store at the pair's
second-member init). It was matched as the `unsigned char` (`E`)
instantiation; the bytes cannot tell `unsigned char` from `bool`, but the
incremental-link thunk table can:

- Its ILT 0x0001859D (`?j_0001859d`, target 0x000F7310):
  `ilt_oracle check` CONFIRMS (exact) the `bool` spelling
  `??A?$hash_map@VAsciiString@@_NU?$hash@VAsciiString@@@rts@@U?$equal_to@VAsciiString@@@3@V?$allocator@U?$pair@$$CBVAsciiString@@_N@_STL@@@_STL@@@_STL@@QAEAA_NABVAsciiString@@@Z`
  and CONTRADICTS the `unsigned char` spelling it carried.
- Its only unwind action, retail funclet 0x00BFBDF0, destroys the
  temporary value_type by `jmp` ILT 0x000479D3. There ilt_oracle CONFIRMS
  `??1?$pair@$$CBVAsciiString@@_N@_STL@@QAE@XZ` (exact) and CONTRADICTS
  `pair<const AsciiString,unsigned char>` (a search over 28 candidate
  mapped types found only `bool`).

Two independent ILT slots agree on `bool`. With T = bool the TU compiles to
the same 142 bytes and the funclet's native label binds to 0x000479D3.
The `unsigned char` claim is retired.
