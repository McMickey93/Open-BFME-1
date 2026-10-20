# 0x00633760: _Rb_tree<AsciiString,...>::erase(iterator, iterator)

The 156-byte body at 0x00633760 was claimed by the generated tgrid row
`?erase@?$_Rb_tree@UGen_t_00076a90_k4@@...` (game/gen_small/tgrid_124.cpp), whose
element type `Gen_t_00076a90_k4` was a placeholder for an unknown 4-byte key.

Retail decides the element type:

- +0x29 calls ILT 0x0002900F, which jumps to 0x00076A90, the matched
  `_Rb_tree<AsciiString,...>::_M_erase` (AsciiStringSetEraseNodes.cpp,
  identity_evidence/0038c0e0-00076a90-asciistring-set-tree.md). The placeholder
  `_M_erase` the generated body names has no pin, so the gen-alias row failed
  the twin check (body_guard_baseline `genalias,0x00633760`).
- +0x76 destroys each removed value through ILT 0x0000D828 (`??1AsciiString`)
  before returning the 0x14-byte node to `__node_alloc`, the same node shape
  as 0x00076A90.

So the key is `AsciiString` and the body is STLport's range erase of
`set<AsciiString>`. The explicit instantiation in AsciiStringSetEraseNodes.cpp
compiles byte-exact (156/156, relocations masked) with real callee names.

The exact source, appended to AsciiStringSetEraseNodes.cpp:

    template void AsciiStringSetTree::erase( AsciiStringSetTree::iterator, AsciiStringSetTree::iterator );

Landing is refused: add_match neither replaces a `gen-alias` tgrid row
(`--replace-rva`: not a supported generated scaffold) nor corrects one
(`--correct-identity`: not a real-source claim). Recorded as a false-reject.
