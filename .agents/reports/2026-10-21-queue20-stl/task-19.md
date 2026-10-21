# Queue 19: unsigned-short/int tree insertion

The two queued authored caller exclusions already landed on master in
66ac6e1a994232c9a559433e4f4d760d460681f7. This task confirms their current
state rather than duplicating that source change. COFF inspection confirms
neither Rva003A4390NameGetter nor STLUnsignedShortIntTreeInsertUnique defines
the four-argument insertion symbol. The canonical provider,
`stlport_rb_tree_ushort_int_insert.cpp`, defines the 178-byte body at
0x0037B600. Its nodepool, construction and rebalance relocations are present.

`./build.sh` over these three sources passes 12/12 functions and all scoped
reference/body guards (10 caller rows, one insert_unique row, one owner row).
The historical census has 18 copies, of which 17 are wrong; numerous generated
emitters remain. `link_check.py --census-only` reports selected-not-retail for
all three files, 0/3 linking. Before/after are identical: no source changed.
The prior master commit also explicitly reported UNKNOWN current selection,
not a whole-game gain. No generated source, pin, header or baseline was edited.

Status: queued caller cleanup was already landed by another contributor;
remaining global selection is blocked. This commit adds verified findings,
not new matching bytes or a complete LINKED claim. The re_log locator is the
synthetic queue key, not a retail function boundary.
