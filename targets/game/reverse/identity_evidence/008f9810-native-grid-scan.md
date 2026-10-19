# Masked grid-cell search at 0x008F9810

The complete BFME1 body is 259 bytes: RET12 at +0x100 ends at
0x008F9913, followed by INT3 padding. The public forwarder at 0x008F7450
adjusts the receiver by +0x10 and tail-jumps here. Existing shroud-manager
constructor and grid-accessor evidence establishes the +0x24 width, +0x28
height and +0x2C cell pointer. This routine reads its own scale at +0x1C;
the neighbouring Gen_008F7CD0 view uses +0x20, so that class is not substituted.
The existing address-derived Rva008F9810Owner and method spelling are retained.
No original lexical class or method identity is claimed.

The retail body accepts a nonzero mask and signed index 0 or 1, confines the
mask to 16 bits, and scans width*height cells of 0x68 bytes. For each set bit
it adds one unsigned word starting at cell+6+2*index, advancing three words
per bit. CMP/JBE at +0x86/+0x8A proves the unsigned running maximum and keeps
the earliest cell on ties. A signed pointer difference divided by 0x68 is
converted to an unsigned cell index; unsigned DIV at +0xB5 and +0xD7 produces
column and row. The +0x1C scale multiplies those results. Three float outputs
are stored, with the last lane cleared to zero. There are no direct callees.

The previous bank already recovered these layouts and arithmetic facts but
compiled to 256 bytes with different persistent mask/index registers.
Open-BFME-2 commit d8961f14c218725a3dc0890fe1dcc313d533d469 contains the
native loop structure in Code/GameEngine/Source/Common/BfmeCellSum.cpp,
Gen_008F7CD0::rva0073BC60 at 0x0073BC60 (262 bytes). Its grid has 0xA8-byte
cells, three indices, a 20-bit mask and four-word steps. Adapting only those
constants and preserving the BFME1 bank's owner/ABI reproduces all 259 bytes.
The change also keeps each coordinate division at its output store, matching
the retail reload after the first store. Ordinary `out->z = 0.0f` is exact;
no integer-punned store or assembly is needed.

Validation: the entire new TU passes build.sh, including both unsigned-to-float
correction references, all DIR32 operands and the body guard. No callee pin,
alias, shared header, generated source or baseline is changed.
