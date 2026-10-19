// cl: /O2 /G6 /DNDEBUG /MD
// Retail 0x009AE6A0 (2107 B; ret at +0x83A, int3 after), cdecl leaf, no
// direct callers: deblocks one band of 8x8 blocks of a decoded video plane.
// For each block edge (rows, then columns from the second block on) it reads
// ten samples across the edge, accumulates the activity on each side into the
// per-block variance array at state+0x28, and either smooths the edge with a
// rolling 8-tap sum (both sides flat and the step under the quantizer limit)
// or applies a bounded correction from the table at state+0x38 through the
// clamp table. Ported from Open-BFME-2's matched 0x001BF090 (its VP6 clean-room
// spec 001bf090.md): the bodies differ only in relocations, BFME2 addressing
// the clamp table at its zero point and this repo's datum starting 256 bytes
// before it. Address-derived name.

struct Rva009AE6A0State
{
	unsigned char m_pad00[0x0C];
	int m_frameQIndex;
	unsigned char m_pad10[0x28 - 0x10];
	int *m_variance;
	unsigned char m_pad2c[0x38 - 0x2c];
	int *m_bounding;
};

extern unsigned char g_bfmeClampTable[];			// retail 0x01356EE0; zero point at +256

void __cdecl filterBand009AE6A0(Rva009AE6A0State *ctx,
	unsigned char *source, unsigned char *destination, unsigned int stride,
	unsigned int count, unsigned int first, const unsigned int *limits)
{
	unsigned int index;
	int x[10];
	int k;
	int upper, lower, sum, filter;
	int qStep, limit;
	unsigned int row;
	unsigned char *rowInput, *rowOutput;
	index = first;
	int p2 = 2 * stride;
	int p3 = 3 * stride;
	int p4 = 4 * stride;
	int p5 = 5 * stride;
	qStep = limits[ctx->m_frameQIndex];
	while (index < first + count) {
		rowInput = source + 8 * (index - first);
		rowOutput = destination + 8 * (index - first);
		for (row = 0; row < 8; ++row) {
			x[0] = rowInput[-p5];
			x[1] = rowInput[-p4];
			x[2] = rowInput[-p3];
			x[3] = rowInput[-p2];
			x[4] = rowInput[-(int)stride];
			x[5] = rowInput[0];
			x[6] = rowInput[stride];
			x[7] = rowInput[p2];
			x[8] = rowInput[p3];
			x[9] = rowInput[p4];
			int tailSample = x[9];
			upper = lower = 0;
			for (k = 0; k < 4; k++) {
				upper += (x[k + 1] - x[k]) > 0 ? (x[k + 1] - x[k]) : (x[k] - x[k + 1]);
			}
			for (k = 0; k < 4; k++) {
				lower += (x[k + 5] - x[k + 6]) > 0 ? (x[k + 5] - x[k + 6]) : (x[k + 6] - x[k + 5]);
			}
			ctx->m_variance[index] += upper > 255 ? 255 : upper;
			ctx->m_variance[index + count] += lower > 255 ? 255 : lower;
			limit = ((qStep * 3) >> 2);
			if (upper < limit && lower < limit && x[5] - x[4] < qStep && x[4] - x[5] < qStep) {
				sum = x[4] + 3 * x[0] + x[3] + x[2] + 4 + x[1];
				rowOutput[-p4] = (unsigned char)((sum + x[1]) >> 3);
				sum += x[5] - x[0];
				rowOutput[-p3] = (unsigned char)((sum + x[2]) >> 3);
				sum += x[6] - x[0];
				rowOutput[-p2] = (unsigned char)((sum + x[3]) >> 3);
				sum += x[7] - x[0];
				rowOutput[-(int)stride] = (unsigned char)((sum + x[4]) >> 3);
				sum += x[8] - x[1];
				rowOutput[0] = (unsigned char)((sum + x[5]) >> 3);
				sum += tailSample - x[2];
				rowOutput[stride] = (unsigned char)((sum + x[6]) >> 3);
				sum += tailSample - x[3];
				rowOutput[p2] = (unsigned char)((sum + x[7]) >> 3);
				sum += tailSample - x[4];
				rowOutput[p3] = (unsigned char)((sum + x[8]) >> 3);
			} else {
				const unsigned char *clamp = g_bfmeClampTable + 256;
				filter = ctx->m_bounding[(x[3] - x[6] + 3 * (x[5] - x[4]) + 4) >> 3];
				rowOutput[-(int)stride] = clamp[x[4] + filter];
				rowOutput[0] = clamp[x[5] - filter];
				rowOutput[-p4] = rowInput[-p4];
				rowOutput[-p3] = rowInput[-p3];
				rowOutput[-p2] = rowInput[-p2];
				rowOutput[stride] = rowInput[stride];
				rowOutput[p2] = rowInput[p2];
				rowOutput[p3] = rowInput[p3];
			}
			rowInput++;
			rowOutput++;
		}
		if (index == first) {
			index++;
			continue;
		}
		{
		unsigned int secondOffset = index - first;
		rowInput = rowOutput = destination - 8 * stride + 8 * secondOffset;
		}
		for (row = 0; row < 8; ++row) {
			x[0] = rowInput[-5];
			x[1] = rowInput[-4];
			x[2] = rowInput[-3];
			x[3] = rowInput[-2];
			x[4] = rowInput[-1];
			x[5] = rowInput[0];
			x[6] = rowInput[1];
			x[7] = rowInput[2];
			x[8] = rowInput[3];
			x[9] = rowInput[4];
			upper = lower = 0;
			for (k = 0; k < 4; k++) {
				upper += (x[k + 1] - x[k]) > 0 ? (x[k + 1] - x[k]) : (x[k] - x[k + 1]);
			}
			for (k = 0; k < 4; k++) {
				lower += (x[k + 5] - x[k + 6]) > 0 ? (x[k + 5] - x[k + 6]) : (x[k + 6] - x[k + 5]);
			}
			ctx->m_variance[index - 1] += upper > 255 ? 255 : upper;
			ctx->m_variance[index] += lower > 255 ? 255 : lower;
			limit = (qStep * 3) >> 2;
			if (upper < limit && lower < limit && x[5] - x[4] < qStep && x[4] - x[5] < qStep) {
				int a0 = x[0], a1 = x[1], a2 = x[2], a3 = x[3];
				int a4 = x[4], a5 = x[5], a6 = x[6], a7 = x[7];
				int a8 = x[8], a9 = x[9];
				sum = a4 + 3 * a0 + a3 + a2 + 4 + a1;
				rowOutput[-4] = (unsigned char)((sum + a1) >> 3);
				sum += a5 - a0;
				rowOutput[-3] = (unsigned char)((sum + a2) >> 3);
				sum += a6 - a0;
				rowOutput[-2] = (unsigned char)((sum + a3) >> 3);
				sum += a7 - a0;
				rowOutput[-1] = (unsigned char)((sum + a4) >> 3);
				sum += a8 - a1;
				rowOutput[0] = (unsigned char)((sum + a5) >> 3);
				sum += a9 - a2;
				rowOutput[1] = (unsigned char)((sum + a6) >> 3);
				sum += a9 - a3;
				rowOutput[2] = (unsigned char)((sum + a7) >> 3);
				sum += a9 - a4;
				rowOutput[3] = (unsigned char)((sum + a8) >> 3);
			} else {
				filter = ctx->m_bounding[(x[3] - x[6] + 3 * (x[5] - x[4]) + 4) >> 3];
				rowOutput[-1] = (g_bfmeClampTable + 256)[x[4] + filter];
				rowOutput[0] = (g_bfmeClampTable + 256)[x[5] - filter];
			}
			rowInput += stride;
			rowOutput += stride;
		}
		index++;
	}
}
