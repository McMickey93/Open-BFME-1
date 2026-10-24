// cl: /O2 /DNDEBUG /MD
//
// VP6 filtered block prediction, retail 0x009B5530 (768 bytes, cdecl: decoder
// state, 16-bit output block, block position 0..5). The name is the one
// symbols.csv pins at this address. Picks the golden or last reconstructed
// frame by the block mode, applies the loop-filtered builder when a profile
// and loop-filter mode are set, then unpacks or filters the block by its
// motion vector (bicubic luma when the prediction-filter thresholds allow,
// bilinear chroma).
//
// Ported unchanged from Open-BFME-2 Code/Libraries/Source/VP6/PredictFilteredBlock.cpp
// (commit 11cc55139e), where the same VP6 code is matched for the BFME2 binary.

extern "C" int __cdecl abs(int);
#pragma intrinsic(abs)

struct Rva009C84D0Vp6Context;

struct Rva009B5830MotionVector
{
	short x;
	short y;
};

struct Rva009B5830State
{
	unsigned char pad0[8];
	int mode;
	unsigned char padC[0x24 - 0x0c];
	Rva009B5830MotionVector vectors[6];
	unsigned char pad3c[0x70 - 0x3c];
	int reconIndex;
	int reconStride;
	unsigned char pad78[0x7c - 0x78];
	int vectorShift;
	int vectorMask;
	unsigned char pad84[0x88 - 0x84];
	int frameStride;
	unsigned char pad8c[0x19d - 0x8c];
	unsigned char profile;
	unsigned char pad19e[0x24c - 0x19e];
	unsigned char *goldenFrame;
	unsigned char pad250[0x254 - 0x250];
	unsigned char *lastFrame;
	unsigned char pad258[0x290 - 0x258];
	unsigned char *loopFilteredBlock;
	unsigned char pad294[0x692 - 0x294];
	unsigned char filterMode;
	unsigned char sizeThreshold;
	unsigned int varianceThreshold;
	unsigned char pad698[0x4534 - 0x698];
	unsigned char loopFilterMode;
};

typedef void (__cdecl *Rva009B5530Filter)(unsigned char *, unsigned char *, void *,
	int, int, int, int);
typedef void (__cdecl *Rva009B5530Unpack)(unsigned char *, void *, int);

extern void *g_bfmeSlotB50;
extern void *g_bfmeSlotB54;
extern unsigned char g_bfmeVp6SelectorMap[40];
void __cdecl Rva009C84D0Vp6Filter(Rva009C84D0Vp6Context *context, void *output, int first, int second);	// 0x009C84D0
int __cdecl rva009C8130(const unsigned char *pixels, int stride);	// 0x009C8130, block variance

void __cdecl Rva009B5530Prepare(Rva009B5830State *pbi, void *output, int block)
{
	int offset2;
	unsigned char *source;
	short mvx;
	int yPhase;
	int y;
	unsigned char *base;
	short mvy;
	unsigned int xPhase;
	unsigned int stride;
	unsigned int offset1;
	int x;
	int mask;
	unsigned long limit;

	source = pbi->lastFrame;
	mask = pbi->vectorMask;
	if (((const int *)g_bfmeVp6SelectorMap)[pbi->mode] == 2)
		source = pbi->goldenFrame;

	if (0 != pbi->profile && pbi->loopFilterMode != 0) {
		Rva009C84D0Vp6Filter((Rva009C84D0Vp6Context *)pbi, source + pbi->reconIndex,
			pbi->vectors[block].x, pbi->vectors[block].y);
		base = pbi->loopFilteredBlock;
		stride = 16;
		offset1 = 34;
		offset2 = 34;
		mvx = pbi->vectors[block].x;
		x = mvx;
		xPhase = x & pbi->vectorMask;
		mvy = pbi->vectors[block].y;
		y = mvy;
		yPhase = y & pbi->vectorMask;
	} else {
		mvx = pbi->vectors[block].x;
		x = mvx;
		mvy = pbi->vectors[block].y;
		xPhase = mvx & mask;
		y = mvy;
		yPhase = y & mask;
		base = pbi->frameStride * ((y + ((y >> 31) & mask)) >> pbi->vectorShift)
			+ pbi->reconIndex
			+ source
			+ ((x + ((x >> 31) & mask)) >> pbi->vectorShift);
		stride = pbi->reconStride;
		offset2 = 0;
		offset1 = 0;
	}

	if (xPhase != 0)
		offset2 += (0 < mvx) * 2 - 1;
	if (yPhase != 0)
		offset2 += ((mvy > 0) * 2 - 1) * stride;

	if (offset1 != offset2) {
		if (4 > block) {
			xPhase <<= 1;
			yPhase <<= 1;
			if (0 == pbi->profile) {
				((Rva009B5530Filter)g_bfmeSlotB54)(base + offset1, base + offset2,
					output, stride, xPhase, yPhase, 0);
			} else if (pbi->filterMode == 2) {
				if (pbi->sizeThreshold > 0)
					// Retail x86 masks the shift count to five bits.
					limit = (1UL << (pbi->sizeThreshold - 1)) << 2;
				else
					limit = 128;
				// Both arms use the captured signed Y value. Keeping the profile
				// split preserves the native local lifetimes before tail merging.
				if ((0 != pbi->sizeThreshold && (abs(x) > limit || ((pbi->profile) ? (abs((int)mvy)) : (abs(y))) > limit))) {
					((Rva009B5530Filter)g_bfmeSlotB54)(base + offset1, base + offset2,
						output, stride, xPhase, yPhase, 0);
				} else if (pbi->varianceThreshold != 0) {
					((Rva009B5530Filter)g_bfmeSlotB54)(base + offset1, base + offset2,
						output, stride, xPhase, yPhase,
						rva009C8130(base + offset1, stride) >= pbi->varianceThreshold);
				} else {
					((Rva009B5530Filter)g_bfmeSlotB54)(offset1 + base, base + offset2,
						output, stride, xPhase, yPhase, 1);
				}
			} else {
				((Rva009B5530Filter)g_bfmeSlotB54)(offset1 + base, base + offset2,
					output, stride, xPhase, yPhase, pbi->filterMode == 1);
			}
		} else {
			((Rva009B5530Filter)g_bfmeSlotB54)(base + offset1, base + offset2,
				output, stride, xPhase, yPhase, 0);
		}
	} else {
		((Rva009B5530Unpack)g_bfmeSlotB50)(offset1 + base, output, stride);
	}
}
