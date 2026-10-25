// cl: /O2 /G6 /DNDEBUG /MD
// BFME 1 body at RVA 0x009A5F50 (475 bytes), dispatch slot 0 (VA 0x01356E60).
// Identity and codegen evidence: the BFME 2 clean-room unit
// Code/Libraries/Source/VP6/FilterMath.cpp at donor revision
// ce1b975697c2f20e514174e3875f8820d1dba612, function PlaneAddNoise_C at
// 0x001B69C0 (475 bytes). The BFME 2 dispatch unit
// PostProcMachineSpecificConfig.cpp declares that function as the body
// formerly address-named d_009a5f50; BFME 1's BfmeCodecCpuDispatch.cpp stores
// its own slot[0] from the same placeholder. The donor body is exact against
// BFME 1 outside its relocation fields (probe: 475/475 bytes, 12 relocs, no
// differences), and the BFME 1 callers prove the same five-argument cdecl
// contract (installer 0x009B0D60, caller 0x009A6130).
//
// The donor's Gaussian helper is a separate matched BFME 1 row
// (?bfmeGaussPdf@@YANNNN@Z at 0x009A5F00, 65 bytes), so its body is inlined
// here by hand with the same expression the donor's inliner substitutes. The
// reference-bound lower/negFirst temporaries are substantive: they give
// retail's preheader int and separate byte negation in the pixel loop.
#include <stdlib.h>
#include <math.h>

// ?d_009a5f50@@YAXXZ converted to its proven C identity.
extern "C" void __cdecl PlaneAddNoise_C(unsigned char *start, unsigned width, unsigned height, int pitch, int q)
{
	unsigned i;
	unsigned j;
	double sigma;
	double x;
	int next;
	signed char dist[300];
	unsigned char noise[2048];
	signed char first;

	sigma = 1 + 0.012698412698412698 * (63 - q);
	next = 0;
	for (x = -32; x < 32; x++) {
		int count = (int)(256 * (exp(-((x - 0) * (x - 0)) / (sigma * sigma + sigma * sigma)) / (sigma * sqrt(6.2831853))) + 0.5);
		if (count) {
			int k;
			for (k = 0; k < count; k++)
				dist[next + k] = (signed char)(int)x;
			next += k;
		}
	}
	for (; next < 256; next++)
		dist[next] = 0;
	for (i = 0; i < 2048; i++)
		noise[i] = dist[rand() & 0xff];
	first = dist[0];
	for (j = 0; j < height; j++) {
		unsigned char *noisePtr = &noise[rand() & 0xff];
		unsigned char *row = start + j * pitch;
		for (i = 0; i < width; i++) {
			const int &lower = -first;
			const signed char &negFirst = -first;
			if (row[i] < lower)
				row[i] = negFirst;
			if (row[i] > 255 - first)
				row[i] = 255 - first;
			row[i] += noisePtr[i];
		}
	}
}
