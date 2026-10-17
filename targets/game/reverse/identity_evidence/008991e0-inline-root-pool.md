# RVA 008991E0: value-family release slot

Retail vtables VA 01135D68 and 011360A8 both place this body in slot 1.
Slot 0 reaches RVA 008991B0, which increments the twelve-bit count in
bits 16..27 and saturates at 0xFFF. This body decrements the same count,
saturates underflow, and only registers a value on the transition to zero.
Bit 30 prevents a second registration. Slot 2 is dispatched when the pool
is full; it differs between the two tables. These observations justify the
reference-count operations, but not a recovered EA class identity. The
existing bank's Rva00899560Value address-qualified family is retained.

The complete body ends with the tail JMP [EAX+8] at +75, ending +78 (120
bytes), followed by alignment. There are no direct callees. The single
DIR32 operand reads VA 01337810. Apt.cpp already defines the twelve-byte
{capacity, count, items} registry pointer as g_rva01337810GcRoots, which
is reused here without a new symbol pin or data alias. The retail source
path reported by brief.py is Libraries/Source/Apt/AptValue.cpp.

The preferred bank matched 119 of 120 nonrelocation bytes. Its second
capacity comparison loaded memory instead of reusing EDI. It also forced
two volatile reads. Moving the failure-side flag clear into an inlined
pool append, called directly through the global pointer, preserves the
retail redundant comparisons and failure-first block placement. The pool
append returns its inserted index or -1; the caller discards that result.
Explicit expansion with __forceinline keeps this small operation inline
under the TU's existing compiler options. Ordinary m_flags reads reproduce
all bytes; neither volatile access is retained. The source-level helper is
a reconstruction choice, not a separately claimed retail function.

Probes of index-return, next-index-local and bool-like-return helpers all
reproduce 120 bytes. The final source uses the index-return form. add_match
and the scoped build verify all bytes and the existing global binding.
