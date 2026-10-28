# 0x00784A70: RefHandle008958D0 destructor

ILT 0x000463AD jumps to the 35-byte body at RVA 0x00784A70. The body loads
the handle's one pointer from `this`, calls the decrement helper at
0x00894D90 on it, and when that returns zero calls bfmeDropA at 0x00895320.

Two matched unwind funclets reach it as the handle destructor:

- 0x00C570B8 (`$L458`, parent `Rva00893030Manager::rva00895950`, 0x00895950):
  `mov ecx,[ebp+4]; jmp 0x000463AD`, unwinding the parent's
  `RefHandle008958D0` local at ebp+4.
- 0x00C570E8 (`$L577`, parent `Rva00893030Manager::rva00895A00`, 0x00895A00):
  the same shape on that parent's handle.

Both parents compile byte-exact with the funclet relocation naming
`??1RefHandle008958D0@@QAE@XZ`, and symbols.csv already pins that name to
ILT 0x000463AD on the strength of the parent handler stub. Retail was linked
without identical-COMDAT folding, so an address has one identity. The opaque
row `?bfmeCleanup@Rva00784A70Cleanup@@QAEXXZ` was an over-claim of the same
body: the destructor is the identity, and the class keeps its address-derived
name.

`BfmeFixup008A2580.cpp`'s inline copy of the destructor is the same call
form and the census proved it retail. The Apt TUs at 0x00893030.. inline the
drop into their copies because their parents need it inline. Their
select-any copies come earlier in link order than BfmeFixup's, so the link
kept a non-retail copy (link queue wrong_selected).
