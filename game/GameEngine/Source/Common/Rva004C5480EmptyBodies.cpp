// cl: /O2 /MD
// Empty bodies no row claimed: a lone `ret` after int3 padding, each
// referenced from data or a code immediate (callback tables, a one-slot
// vtable at 0x0113D074, and teardowns registered with atexit by static
// initializers). Retail links without identical-COMDAT folding, so every one
// is its own body; all keep address-derived names.

void Rva004C5480Empty() {}
void Rva004E25E0Empty() {}
void Rva00642E10Empty() {}
void Rva00642E20Empty() {}
void Rva00642FB0Empty() {}
void Rva00783250Empty() {}
void Rva00783260Empty() {}
void Rva00863280Empty() {}
void Rva008717A0Empty() {}
void Rva008F9330Empty() {}
void Rva009471D0Empty() {}
void Rva009A7030Empty() {}
void Rva009A91C0Empty() {}
void Rva00C6FFB0Empty() {}
void Rva00C708B0Empty() {}
void Rva00C708C0Empty() {}
void Rva00C70AE0Empty() {}
void Rva00C70AF0Empty() {}
void Rva00C70B80Empty() {}
void Rva00C70B90Empty() {}
