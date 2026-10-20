# 0x000EEF40: const _Rb_tree find over a set of 4-byte keys

ILT 0x00016C70 jumps to the 71-byte body at RVA 0x000EEF40. It has two retail callers:

- `Team::bfmeSetNeedsGateOpenRaw` at 0x000F1950 (call at +0x2C): it looks up the gate ID in the Team+0x104 set. On a hit, it erases the node inline and frees it with `push 0x14` (a 20-byte node). On a miss, it inserts through the matched `insert_unique` at 0x000EEC50, whose ledger name gives the key type as `Rva000EEC50Key`.
- `Gen_00371090::bfmeRemove` at 0x00371090 (call at +0x25): it erases inline and frees the node with `push 0x14` at +0x56. Its own source declares the member as `_STL::set<NameKeyType>` and casts it to `map<NameKeyType, Real>` only to reach the legacy pin.

STLport `_Rb_tree_node` is a 16-byte base plus the value. A 20-byte node therefore holds a 4-byte value, which means a set. A `map<NameKeyType, float>` node would be 24 bytes. The legacy pin `??$find@W4NameKeyType@@@?$_Rb_tree@W4NameKeyType@@U?$pair@$$CBW4NameKeyType@@M@...` at 0x000EEF40 names a map that neither caller has, so it should be drained.

The Team body compiles byte-exact (277/277) against this set find. The override admits that spelling at the ILT the Team caller encodes:

pin-identity-override: ??$find@W4Rva000EEC50Key@@@?$_Rb_tree@W4Rva000EEC50Key@@W41@U?$_Identity@W4Rva000EEC50Key@@@_STL@@U?$less@W4Rva000EEC50Key@@@3@V?$allocator@W4Rva000EEC50Key@@@3@@_STL@@QBE?AU?$_Rb_tree_iterator@W4Rva000EEC50Key@@U?$_Const_traits@W4Rva000EEC50Key@@@_STL@@@1@ABW4Rva000EEC50Key@@@Z 0x00016C70 caller=0x000F1950 Team::bfmeSetNeedsGateOpenRaw REL32 at +0x2C encodes ILT 0x00016C70; both callers free 20-byte set nodes, so the map pin at 0x000EEF40 is the wrong identity
