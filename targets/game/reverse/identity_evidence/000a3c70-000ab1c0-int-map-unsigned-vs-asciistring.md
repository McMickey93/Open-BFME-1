# map<Int,UnsignedInt> vs map<Int,AsciiString> tree members (PSPlayerStats vs ignore lists)

Retail has two parallel chains of STLport `_Rb_tree` members for int-keyed
maps whose node is 0x18 bytes (16-byte header, 8-byte pair). Before this
correction the ledger put the `map<Int,UnsignedInt>` names (`$$CBHI`) on the
AsciiString chain and left the real UnsignedInt chain under generated or
address-tagged names. Retail was linked without identical-COMDAT folding, so
each name has exactly one body.

## Which chain is which

The value type shows in the chains' leaf helpers:

- `_Construct` behind ILT 0x1C67A (body 0x000A9EA0) sets up an EH frame and
  copies the second dword through a constructor: the value is a 4-byte class,
  AsciiString. `_Construct` behind ILT 0x2C3A4 (body 0x000A36F0) is a bare
  two-dword copy: POD.
- `_M_erase` at 0x000AA7B0 (reached via ILT 0x4887E) calls the pair destructor
  at `[node+0x10]` through ILT 0x240F before freeing each 0x18-byte node.
  `_M_erase` at 0x000A3660 (via ILT 0x47C58) frees nodes without destroying
  anything: POD.
- `_M_copy` at 0x000AAC70 (via ILT 0x42BB3) clones through ILT 0x1C67A (the
  AsciiString `_Construct`). `_M_copy` at 0x000A3E50 (via ILT 0x41281) clones
  through ILT 0x2C3A4 (POD).
- The destructor at 0x000AB1C0 and `operator=` at 0x004EE0E0 call
  0x4887E/0x42BB3 (the AsciiString chain). The destructor at 0x000A3C70 and
  `operator=` at 0x000A4BB0 call 0x47C58/0x41281 (the POD chain).

## Callers

- The POD chain is what PSPlayerStats uses. The matched `~PSPlayerStats`
  (0x000A5150) calls the destructor through ILT 0x9895 -> 0x000A3C70, and the
  matched `PSPlayerStats::operator=` (0x000A5950) calls `operator=` through ILT
  0x13B33 -> 0x000A4BB0. Zero Hour's
  GameSpy/PersistentStorageThread.h declares
  `typedef std::map<Int, UnsignedInt> PerGeneralMap;` for exactly these 27
  PSPlayerStats members. The symbols.csv pins already name those ILTs
  `map<Int,UnsignedInt>`.
- The AsciiString chain is the ignore list's
  `SavedIgnoreMap = std::map<Int, AsciiString>` (Zero Hour PeerDefs.h). The
  matched `~GameSpyInfo`, `GameSpyInfo::loadSavedIgnoreList` and
  `refreshIgnoreList` call its destructor through ILT 0xE02F -> 0x000AB1C0 and
  its `operator=` through ILT 0x46DD -> 0x004EE0E0, spelled as
  `map<Int,AsciiString>` in their objects. The symbols.csv pins at 0xE02F and
  0x46DD already carry those names.

## Corrections

| RVA | size | old name | new name |
|---|---|---|---|
| 0x000A3C70 | 124 | ??1 _Rb_tree<int,pair<const int,Gen_t_000a3c70_p4pod>> (gen-tgrid) | ??1 _Rb_tree<int,pair<const int,unsigned>> |
| 0x000A4BB0 | 178 | ??4 _Rb_tree<int,pair<const int,Gen_t_000a4bb0_p12cd>> (gen-tgrid) | ??4 _Rb_tree<int,pair<const int,unsigned>> |
| 0x000A3660 | 53 | _M_erase <..Gen_t_000a3660_p4pod> (gen-tgrid) | _M_erase <int,pair<const int,unsigned>> |
| 0x000A3E50 | 171 | _M_copy <..Rva000A3E50Value> | _M_copy <int,pair<const int,unsigned>> |
| 0x000AB1C0 | 124 | ??1 <int,pair<const int,unsigned>> | ??1 <int,pair<const int,AsciiString>> |
| 0x004EE0E0 | 178 | ??4 <int,pair<const int,unsigned>> | ??4 <int,pair<const int,AsciiString>> |
| 0x000AAC70 | 171 | _M_copy <int,pair<const int,unsigned>> | _M_copy <int,pair<const int,AsciiString>> |
| 0x000AA7B0 | 61 | _M_erase <Gen_t_000aa7b0_k4,...p4pod> (gen-tgrid) | _M_erase <int,pair<const int,AsciiString>> |
| 0x0004887E | 5 | _M_erase <int,pair<const int,unsigned>> (ILT row) | retired: the ILT jumps to the AsciiString `_M_erase` at 0x000AA7B0 |

The three symbols.csv pins that put `map<Int,UnsignedInt>` names on
AsciiString-chain ILTs move to the POD-chain ILTs: `_Construct` 0x1C67A ->
0x2C3A4, `_M_copy` 0x42BB3 -> 0x41281, `_M_erase` 0x4887E -> 0x47C58.

Mangled names:
`??1?$_Rb_tree@HU?$pair@$$CBHI@_STL@@U?$_Select1st@U?$pair@$$CBHI@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHI@_STL@@@2@@_STL@@QAE@XZ`,
`??4?$_Rb_tree@HU?$pair@$$CBHI@_STL@@U?$_Select1st@U?$pair@$$CBHI@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHI@_STL@@@2@@_STL@@QAEAAV01@ABV01@@Z`,
`?_M_copy@?$_Rb_tree@HU?$pair@$$CBHI@_STL@@U?$_Select1st@U?$pair@$$CBHI@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHI@_STL@@@2@@_STL@@AAEPAU?$_Rb_tree_node@U?$pair@$$CBHI@_STL@@@2@PAU32@0@Z`,
`?_M_erase@?$_Rb_tree@HU?$pair@$$CBHI@_STL@@U?$_Select1st@U?$pair@$$CBHI@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHI@_STL@@@2@@_STL@@AAEXPAU?$_Rb_tree_node@U?$pair@$$CBHI@_STL@@@2@@Z`
and the same four with `$$CBHVAsciiString@@` in place of `$$CBHI`.
The address-tagged `_M_copy` row name was
`?_M_copy@?$_Rb_tree@HU?$pair@$$CBHURva000A3E50Value@@@_STL@@U?$_Select1st@U?$pair@$$CBHURva000A3E50Value@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHURva000A3E50Value@@@_STL@@@2@@_STL@@AAEPAU?$_Rb_tree_node@U?$pair@$$CBHURva000A3E50Value@@@_STL@@@2@PAU32@0@Z`.

Approved by the project lead 2026-10-16 (link queue #48/#73).
