// cl: /O2 /DNDEBUG /DWIN32 /MD /EHsc
//
// Two unreferenced 10-byte __thiscall bodies, each alone in an int3-padded
// gap, that call the pinned table scan 0x00892FD0 on the SAME receiver (ecx
// is passed through untouched) with a fixed key pair and return its bool:
//
//     push 2 / push 4 (or 3) / call 0x00892FD0 / ret
//
// The scan (ret 8, reads a count at +0 and 8-byte entries at +8) answers
// whether every entry's +4 key is one of the two arguments. The pin's class
// is the generated name the 0x00896710 caller reaches it through.
//
// IDENTITY IS NOT RECOVERED. Member names are derived from addresses.

class Gen_uw_00893e70
{
public:
	bool Rva00892FD0( int first, int second );
	bool rva00893020();
	bool rva008951F0();
};

bool Gen_uw_00893e70::rva00893020()
{
	return Rva00892FD0( 4, 2 );
}

bool Gen_uw_00893e70::rva008951F0()
{
	return Rva00892FD0( 3, 2 );
}
