// cl: /O2 /G6 /DNDEBUG /MD
// BFME 1 body at RVA 0x009A8C50 (1047 bytes). Identity and codegen evidence:
// the BFME 2 clean-room unit Code/Libraries/Source/VP6/UpdateUMVBorder.cpp at
// donor revision ce1b975697c2f20e514174e3875f8820d1dba612, whose linked retail
// body at 0x001B96A0 (1047 bytes) is byte-identical to the BFME 1 body outside
// its four relocation fields (exact masked comparison, no differences). The
// BFME 1 callers Rva009A9070CopyStreams and Rva009AA8F0Dispatch independently
// prove a two-argument cdecl helper (context, frame/offset). See
// targets/game/reverse/identity_evidence/009a8c50-update-umv-border.md.
//
// UpdateUMVBorder: extends each plane of a reconstruction frame into its border
// by replication. For Y the left and right edge pixels of every row are
// replicated MVBorder bytes outwards, then the first and last picture rows are
// copied over the MVBorder rows above and below. U and V do the same with half
// the border.
//
// One set of four pointers serves every phase (side fills and row copies);
// the U/V row copies address the bottom row through the top pointer, which is
// what gives retail's merged destination with its recomputed border*stride.

struct UpdateUMVBorderInstance
{
	unsigned char m_pad0[0x78];
	int m_reconYDataOffset;
	int m_reconUDataOffset;
	int m_reconVDataOffset;
	unsigned char m_pad1[0x90 - 0x84];
	int m_hFragments;
	int m_vFragments;
	int m_yStride;
	int m_uvStride;
	unsigned char m_pad2[0xb4 - 0xa0];
	int m_mvBorder;
};

extern "C" void *memset(void *, int, unsigned);
extern "C" void *memcpy(void *, const void *, unsigned);
#pragma intrinsic(memset, memcpy)

extern "C" void UpdateUMVBorder(UpdateUMVBorderInstance *pbi, unsigned char *buffer)
{
	int i;
	int rows;
	int border;
	int stride;
	int uvBorder;
	unsigned char *srcLeft, *srcRight, *dstLeft, *dstRight;

	rows = pbi->m_vFragments * 8;
	border = pbi->m_mvBorder;
	stride = pbi->m_yStride;
	srcLeft = pbi->m_reconYDataOffset + buffer;
	srcRight = srcLeft + pbi->m_hFragments * 8 - 1;
	dstLeft = srcLeft - border;
	dstRight = srcRight + 1;
	for (i = 0; i < rows; i++) {
		memset(dstLeft, srcLeft[0], border);
		memset(dstRight, srcRight[0], border);
		srcLeft += stride;
		srcRight += stride;
		dstLeft += stride;
		dstRight += stride;
	}
	srcLeft = buffer + border * stride;
	srcRight = srcLeft + (pbi->m_vFragments * 8 - 1) * stride;
	dstLeft = buffer;
	dstRight = srcRight + stride;
	for (i = 0; i < border; i++) {
		memcpy(dstLeft, srcLeft, stride);
		memcpy(dstRight, srcRight, stride);
		dstLeft += stride;
		dstRight += stride;
	}

	stride = pbi->m_uvStride;
	rows = pbi->m_vFragments * 4;
	srcLeft = buffer + pbi->m_reconUDataOffset;
	srcRight = srcLeft + pbi->m_hFragments * 4 - 1;
	uvBorder = (unsigned)border / 2;
	dstLeft = srcLeft - uvBorder;
	dstRight = srcRight + 1;
	for (i = 0; i < rows; i++) {
		memset(dstLeft, srcLeft[0], uvBorder);
		memset(dstRight, srcRight[0], uvBorder);
		srcLeft += stride;
		srcRight += stride;
		dstLeft += stride;
		dstRight += stride;
	}
	srcLeft = buffer + pbi->m_reconUDataOffset - uvBorder;
	srcRight = srcLeft + (pbi->m_vFragments * 4 - 1) * stride;
	dstLeft = srcLeft - uvBorder * stride;
	dstRight = srcRight + stride;
	for (i = 0; i < uvBorder; i++) {
		memcpy(dstLeft, srcLeft, stride);
		memcpy(dstLeft + (dstRight - (srcLeft - ((unsigned)border / 2) * stride)), srcRight, stride);
		dstLeft += stride;
	}

	srcLeft = buffer + pbi->m_reconVDataOffset;
	srcRight = srcLeft + pbi->m_hFragments * 4 - 1;
	dstLeft = srcLeft - uvBorder;
	dstRight = srcRight + 1;
	for (i = 0; i < rows; i++) {
		memset(dstLeft, srcLeft[0], uvBorder);
		memset(dstRight, srcRight[0], uvBorder);
		srcLeft += stride;
		srcRight += stride;
		dstLeft += stride;
		dstRight += stride;
	}
	srcLeft = buffer + pbi->m_reconVDataOffset - uvBorder;
	srcRight = srcLeft + (pbi->m_vFragments * 4 - 1) * stride;
	dstLeft = srcLeft - uvBorder * stride;
	dstRight = srcRight + stride;
	for (i = 0; i < uvBorder; i++) {
		memcpy(dstLeft, srcLeft, stride);
		memcpy(dstLeft + (dstRight - (srcLeft - ((unsigned)border / 2) * stride)), srcRight, stride);
		dstLeft += stride;
	}
}
