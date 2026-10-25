// cl: /O2 /G6 /DNDEBUG /MD
// BFME 1 body at RVA 0x009B18D0 (1526 bytes). Identity and codegen evidence:
// the BFME 2 clean-room unit Code/Libraries/Source/VP6/DeringBlockStrongC.cpp at
// donor revision ce1b975697c2f20e514174e3875f8820d1dba612, whose linked retail
// body at 0x001C22C0 (1526 bytes) is byte-identical to the BFME 1 body outside
// its relocation fields. The donor dispatch unit PostProcMachineSpecificConfig.cpp
// fills slot[16] with this function and slot[24] with DeringBlockStrong_C, exactly
// the two addresses BFME 1's BfmeCodecCpuDispatch fills, and records that both
// previously held address-derived placeholder names. See
// targets/game/reverse/identity_evidence/009b10e0-009b18d0-dering-blocks.md.
//
// The donor's g_vp6SharpenModifier is BFME 1's matched data row
// Vp6FilterEdgeTagTable at VA 0x012D8158 (data_rows.csv
// _Vp6FilterEdgeTagTable), the same 64-entry int table the four matched VP6
// filters already use; the array is only ever indexed, so the layout is fixed.
//
// DeringBlockWeak_C: the weak companion of DeringBlockStrong_C, same six-argument
// cdecl shape; the weight cap is 3 * Q limited to 24 and each output pixel is
// stored immediately, so source/destination overlap behaves as retail.

extern "C" int Vp6FilterEdgeTagTable[64];

static inline int ClampWeight(int weight, int sharpen, int cap)
{
	if (weight < -64)
		return sharpen;
	if (weight < 0)
		return 0;
	if (weight > cap)
		return cap;
	return weight;
}

extern "C" void __cdecl DeringBlockWeak_C(void *instance, const unsigned char *source,
	unsigned char *destination, int pitch, int qIndex, const int *scaleTable)
{
	int quality = scaleTable[qIndex];
	int sharpen = Vp6FilterEdgeTagTable[qIndex];
	const unsigned char *above = source - pitch;
	const unsigned char *below = source + pitch;
	int cap = 3 * quality;
	short vertical[72];
	short horizontal[72];
	unsigned int c;
	int r;

	if (cap > 24)
		cap = 24;

	const unsigned char *vrow = source;
	for (r = 0; r < 9; r++) {
		for (c = 0; c < 8; c++) {
			unsigned char differenceSample001 = vrow[c];
			int differencePromoted002 = differenceSample001;
			unsigned int differencePromoted003 = pitch;
			unsigned int differenceDifference004 = c - differencePromoted003;
			unsigned char differenceSample005 = vrow[differenceDifference004];
			int differencePromoted006 = differenceSample005;
			int differenceDifference007 = differencePromoted002 - differencePromoted006;
			unsigned char differenceSample008 = vrow[c];
			int differencePromoted009 = differenceSample008;
			unsigned int differencePromoted010 = pitch;
			unsigned int differenceDifference011 = c - differencePromoted010;
			unsigned char differenceSample012 = vrow[differenceDifference011];
			int differencePromoted013 = differenceSample012;
			int differenceDifference014 = differencePromoted009 - differencePromoted013;
			unsigned int differencePromoted015 = pitch;
			unsigned int differenceDifference016 = c - differencePromoted015;
			unsigned char differenceSample017 = vrow[differenceDifference016];
			int differencePromoted018 = differenceSample017;
			unsigned char differenceSample019 = vrow[c];
			int differencePromoted020 = differenceSample019;
			int differenceDifference021 = differencePromoted018 - differencePromoted020;
			int difference = (differenceDifference007) > 0 ? (differenceDifference014) : (differenceDifference021);
			int weight;
			int outputValueDifference022 = 16 - difference;
			int outputValueProduct023 = 2 * (outputValueDifference022);
			int outputValueSum024 = quality + outputValueProduct023;
			weight = ClampWeight(outputValueSum024, sharpen, cap);
			int outputIndexProduct025 = r * 8;
			unsigned int outputIndexPromoted026 = outputIndexProduct025;
			unsigned int outputIndexSum027 = outputIndexPromoted026 + c;
			vertical[outputIndexSum027] = (short)weight;
		}
		vrow += pitch;
	}
	const unsigned char *hrow = source;
	for (r = 0; r < 8; r++) {
		for (unsigned int hc = 0; hc < 9; hc++) {
			int differencePromoted028 = hc;
			unsigned char differenceSample029 = hrow[(int)differencePromoted028];
			int differencePromoted030 = differenceSample029;
			int differencePromoted031 = hc;
			int differenceDifference032 = (int)differencePromoted031 - 1;
			unsigned char differenceSample033 = hrow[differenceDifference032];
			int differencePromoted034 = differenceSample033;
			int differenceDifference035 = differencePromoted030 - differencePromoted034;
			int differencePromoted036 = hc;
			unsigned char differenceSample037 = hrow[(int)differencePromoted036];
			int differencePromoted038 = differenceSample037;
			int differencePromoted039 = hc;
			int differenceDifference040 = (int)differencePromoted039 - 1;
			unsigned char differenceSample041 = hrow[differenceDifference040];
			int differencePromoted042 = differenceSample041;
			int differenceDifference043 = differencePromoted038 - differencePromoted042;
			int differencePromoted044 = hc;
			int differenceDifference045 = (int)differencePromoted044 - 1;
			unsigned char differenceSample046 = hrow[differenceDifference045];
			int differencePromoted047 = differenceSample046;
			int differencePromoted048 = hc;
			unsigned char differenceSample049 = hrow[(int)differencePromoted048];
			int difference = (differenceDifference035) > 0 ? (differenceDifference043) : (differencePromoted047 - differenceSample049);
			int weight;
			weight = quality + 2 * (16 - difference);
			if (weight < -64) weight = sharpen;
			else if (weight < 0) weight = 0;
			else if (weight > cap) weight = cap;
			horizontal[r * 9 + (int)hc] = (short)weight;
		}
		hrow += pitch;
	}

	int off = 0;
	for (r = 0; r < 8; r++) {
		for (c = 0; c < 8; c++) {
			int centerPixel = source[off + c];
			int rightPixel = source[off + c + 1];
			int leftPixel = source[off + c - 1];
			int left = horizontal[r * 9 + c];
			int up = vertical[r * 8 + c];
			int down = vertical[r * 8 + c + 8];
			int right = horizontal[r * 9 + c + 1];
			int value = ((128 - right - down - up - left) * centerPixel
				+ down * below[off + c] + left * leftPixel
				+ right * rightPixel + up * above[off + c] + 64) >> 7;
			int pixel;
			if (value < 0) pixel = 0;
			else if (value > 255) pixel = 255;
			else pixel = (int)value;
			destination[off + c] = (unsigned char)pixel;
		}
		off += pitch;
	}
}
