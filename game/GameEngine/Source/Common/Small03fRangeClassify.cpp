// cl: /DNDEBUG /MD /G6 /EHsc
//
// Retail 0x0093C2D0 is a two-band unsigned-short classifier accepting
// [0x0E01, 0x0E3A] and [0x0E3F, 0x0E5B]. The decompile-faithful
// conjunction-of-disjunctions spelling is what emits retail's branch
// layout (`jb +6 / jbe +12 / jb +12 / ja +6` with the `mov eax,1` arm at
// +0x1D); the early-return/goto/nested-guard spellings all move the first
// `jb` target. IDENTITY IS NOT RECOVERED: the owner keeps its address
// token.
class Rva0093C2D0Owner
{
public:
	static int classify(unsigned short v);
};

int Rva0093C2D0Owner::classify(unsigned short v)
{
	if ((v < 0x0E01 || v > 0x0E3A) && (v < 0x0E3F || v > 0x0E5B))
		return 0;
	return 1;
}

// Retail 0x0093C300 (unreferenced, after int3 padding, directly after the
// classifier): `fld dword ptr [0x01075334] / ret`, returning the 1.0f the
// recorded .rdata float g_bfmeDefaultBU holds. A literal 1.0f would emit
// fld1, so the load is of the datum. Address-derived name.
extern float g_bfmeDefaultBU;

float Rva0093C300GetOne()
{
	return g_bfmeDefaultBU;
}
