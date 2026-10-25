// cl: /O2 /G6 /DNDEBUG /MD
// BFME 1 body at RVA 0x009B2190 (916 bytes), caller-less in both games.
// Identity and codegen evidence: the BFME 2 clean-room unit
// Code/Libraries/Source/VP6/DiagonalBlur.cpp at donor revision
// ce1b975697c2f20e514174e3875f8820d1dba612, whose linked retail body at
// 0x001C2B80 (916 bytes) is byte-identical to the BFME 1 body outside its four
// relocation fields (exact masked comparison, no diffs). The BFME 1 disassembly
// independently reads arguments 2, 3 and 4 and no first argument, agreeing with
// this cdecl signature. See
// targets/game/reverse/identity_evidence/009b2190-diagonal-blur.md.
//
// Two-pass 8x8 filter. Pass 1 blurs a block with its four diagonal neighbours
// one pixel away (weight 4) and two pixels away (weight 2); pass 2 continues
// eight rows further down both pointers and sharpens each pixel against its
// four direct neighbours, clamped to 0..255.
// c2 orders commutative operands and SIB base/index by symbol ids, which it
// hands out in 32-id chunks. The second pass's own row and column counters,
// its count-down row loop and the named centre pixel give retail's numbering.
extern "C" void DiagonalBlur(void *instance, unsigned char *source, unsigned char *dest, int pitch)
{
	unsigned char *src = source;
	unsigned char *dst = dest;
	int row, row2, col, col2;
	for (row = 0; row < 8; row++) {
		for (col = 0; col < 8; col++) {
			dst[col] = (unsigned char)((16 + 8 * src[col]
				+ 4 * (src[col - pitch - 1] + src[col + pitch - 1] + src[col - pitch + 1] + src[col + pitch + 1])
				+ 2 * (src[col - 2 * pitch - 2] + src[col + 2 * pitch + 2] + src[col + 2 * pitch - 2] + src[col - 2 * pitch + 2])) >> 5);
		}
		dst += pitch;
		src += pitch;
	}
	row2 = 8;
	while (row2--) {
		for (col2 = 0; col2 < 8; col2++) {
			int center = src[col2];
			int value = (1 + 6 * center - src[col2 - 1] - src[col2 - pitch] - src[col2 + pitch] - src[col2 + 1]) >> 1;
			if (value < 0)
				value = 0;
			else if (value > 255)
				value = 255;
			dst[col2] = (unsigned char)value;
		}
		dst += pitch;
		src += pitch;
	}
}
