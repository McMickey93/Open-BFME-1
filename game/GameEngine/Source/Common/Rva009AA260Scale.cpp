// ?Rva009AA260Scale@@YAHPAURva009AA260Context@@PBEHIIPAEIII@Z
// Retail RVA 009AA260: caller 009AA4F0 pushes nine arguments and cleans 24h.
// Code ends with ret at +253; two 24-byte tables at +254/+26c follow it.
// Callback slots are witnessed by dispatch initialization at RVA009B0FBF.
// The direct-copy callback is the matched 009A91A0 bfmeCopy body; retail
// deliberately invokes it with an ignored fourth cdecl argument. This cast
// preserves that MSVC x86 ABI contract, rather than introducing a wrapper.
// The empty vertical callback address is independently verified as 009A91C0.
// Table destinations (offsets): 52/46/68/3b/68/5e; c7/a5/102/87/102/e6.
// The address-qualified name is intentional: the caller/layout evidence proves
// the scaler family and ABI, but not an original class or public owner.

struct Rva009AA260Context
{
	unsigned char m_pad00[0x58];
	int m_hscale;
	int m_hratio;
	int m_vscale;
	int m_vratio;
};

typedef void (__cdecl *Rva009AA260HorizontalScale)(
	const unsigned char *, unsigned int, unsigned char *, unsigned int);
typedef void (__cdecl *Rva009AA260VerticalScale)(
	unsigned char *, unsigned int, unsigned int);

extern void __cdecl bfmeCopy(const void *, unsigned int, void *);

Rva009AA260HorizontalScale g_Va01356DA4;
Rva009AA260HorizontalScale g_Va01356EB0;
Rva009AA260HorizontalScale g_Va01356E80;
Rva009AA260VerticalScale g_Va01356E7C;
Rva009AA260VerticalScale g_Va01356EA8;
Rva009AA260VerticalScale g_Va01356E70;
Rva009AA260VerticalScale g_Va01356E78;
Rva009AA260VerticalScale g_Va01356E90;
Rva009AA260VerticalScale g_Va01356EA4;

static void __cdecl Rva009A91C0NullScale(
	unsigned char *, unsigned int, unsigned int)
{
}

static Rva009AA260HorizontalScale rva009AA260Horizontal45(void)
{
	return g_Va01356DA4;
}

static Rva009AA260HorizontalScale rva009AA260Horizontal35(void)
{
	return g_Va01356EB0;
}

static Rva009AA260HorizontalScale rva009AA260Horizontal21(void)
{
	return g_Va01356E80;
}

static Rva009AA260VerticalScale rva009AA260Vertical45(void)
{
	return g_Va01356E7C;
}

static Rva009AA260VerticalScale rva009AA260Vertical35(void)
{
	return g_Va01356EA8;
}

static Rva009AA260VerticalScale rva009AA260Vertical21(void)
{
	return g_Va01356E70;
}

static Rva009AA260VerticalScale rva009AA260LastVertical45(void)
{
	return g_Va01356E78;
}

static Rva009AA260VerticalScale rva009AA260LastVertical35(void)
{
	return g_Va01356E90;
}

static Rva009AA260VerticalScale rva009AA260LastVertical21(void)
{
	return g_Va01356EA4;
}

int __cdecl Rva009AA260Scale(
	Rva009AA260Context *context,
	const unsigned char *source,
	int source_pitch,
	unsigned int source_width,
	unsigned int source_height,
	unsigned char *dest,
	unsigned int dest_pitch,
	unsigned int dest_width,
	unsigned int dest_height)
{
	unsigned int i;
	unsigned int k;
	unsigned int source_band_height = 0;
	unsigned int dest_band_height = 0;

	int hscale = context->m_hscale;
	int hratio = context->m_hratio;
	int vscale = context->m_vscale;
	int vratio = context->m_vratio;
	int ratio_scalable = 1;

	Rva009AA260HorizontalScale horizontal_scale = 0;
	Rva009AA260VerticalScale vertical_scale = 0;
	Rva009AA260VerticalScale last_vertical_scale = 0;

	(void)source_height;

	switch (hratio * 10 / hscale)
	{
	case 8:
		horizontal_scale = rva009AA260Horizontal45();
		break;
	case 6:
		horizontal_scale = rva009AA260Horizontal35();
		break;
	case 5:
		horizontal_scale = rva009AA260Horizontal21();
		break;
	case 10:
		horizontal_scale = (Rva009AA260HorizontalScale)bfmeCopy;
		break;
	default:
		ratio_scalable = 0;
		break;
	}

	switch (vratio * 10 / vscale)
	{
	case 8:
		vertical_scale = rva009AA260Vertical45();
		last_vertical_scale = rva009AA260LastVertical45();
		source_band_height = 4;
		dest_band_height = 5;
		break;
	case 6:
		vertical_scale = rva009AA260Vertical35();
		last_vertical_scale = rva009AA260LastVertical35();
		source_band_height = 3;
		dest_band_height = 5;
		break;
	case 5:
		vertical_scale = rva009AA260Vertical21();
		last_vertical_scale = rva009AA260LastVertical21();
		source_band_height = 1;
		dest_band_height = 2;
		break;
	case 10:
		vertical_scale = Rva009A91C0NullScale;
		last_vertical_scale = Rva009A91C0NullScale;
		source_band_height = 4;
		dest_band_height = 4;
		break;
	default:
		ratio_scalable = 0;
		break;
	}

	if (ratio_scalable == 0)
		return ratio_scalable;

	horizontal_scale(source, source_width, dest, dest_width);

	for (k = 0;
		k < (dest_height + dest_band_height - 1) / dest_band_height - 1;
		++k)
	{
		for (i = 1; i < source_band_height; ++i)
		{
			horizontal_scale(
				source + i * source_pitch, source_width,
				dest + i * dest_pitch, dest_width);
		}

		horizontal_scale(
			source + source_band_height * source_pitch, source_width,
			dest + dest_band_height * dest_pitch, dest_width);

		vertical_scale(dest, dest_pitch, dest_width);

		source += source_band_height * source_pitch;
		dest += dest_band_height * dest_pitch;
	}

	for (i = 1; i < source_band_height; ++i)
	{
		horizontal_scale(
			source + i * source_pitch, source_width,
			dest + i * dest_pitch, dest_width);
	}

	last_vertical_scale(dest, dest_pitch, dest_width);
	return ratio_scalable;
}

// Fixed 4:5 scaler. Retail entry 009A9400 follows INT3; RET at 009A954B.
// The nine stack slots and callback ABIs agree with the generic scaler above.
void __cdecl Rva009A9400(
    Rva009AA260Context *, const unsigned char *source, int source_pitch,
    unsigned int source_width, unsigned int, unsigned char *dest,
    unsigned int dest_pitch, unsigned int dest_width, unsigned int dest_height)
{
    unsigned int i, k;
    rva009AA260Horizontal45()(source, source_width, dest, dest_width);
    for (k = 0; k < dest_height / 5 - 1; ++k) {
        for (i = 1; i < 4; ++i)
            rva009AA260Horizontal45()(source + i * source_pitch, source_width,
                dest + i * dest_pitch, dest_width);
        rva009AA260Horizontal45()(source + 4 * source_pitch, source_width,
            dest + 5 * dest_pitch, dest_width);
        rva009AA260Vertical45()(dest, dest_pitch, dest_width);
        source += 4 * source_pitch;
        dest += 5 * dest_pitch;
    }
    for (i = 1; i < 4; ++i)
        rva009AA260Horizontal45()(source + i * source_pitch, source_width,
            dest + i * dest_pitch, dest_width);
    rva009AA260LastVertical45()(dest, dest_pitch, dest_width);
}

// Fixed 3:5 sibling, 009A97B0..009A98DB, likewise bounded by INT3.
void __cdecl Rva009A97B0(
    Rva009AA260Context *, const unsigned char *source, int source_pitch,
    unsigned int source_width, unsigned int, unsigned char *dest,
    unsigned int dest_pitch, unsigned int dest_width, unsigned int dest_height)
{
    unsigned int i, k;
    rva009AA260Horizontal35()(source, source_width, dest, dest_width);
    for (k = 0; k < dest_height / 5 - 1; ++k) {
        for (i = 1; i < 3; ++i)
            rva009AA260Horizontal35()(source + i * source_pitch, source_width,
                dest + i * dest_pitch, dest_width);
        rva009AA260Horizontal35()(source + 3 * source_pitch, source_width,
            dest + 5 * dest_pitch, dest_width);
        rva009AA260Vertical35()(dest, dest_pitch, dest_width);
        source += 3 * source_pitch;
        dest += 5 * dest_pitch;
    }
    for (i = 1; i < 3; ++i)
        rva009AA260Horizontal35()(source + i * source_pitch, source_width,
            dest + i * dest_pitch, dest_width);
    rva009AA260LastVertical35()(dest, dest_pitch, dest_width);
}

// Retail 0x009AA4F0 (606 B), cdecl: scale one decoded frame into the output
// planes. The source extent is the destination's scaled back by each axis
// ratio, the padded extent rounds it up to the ratio's block (3 or 8); luma
// goes through Rva009AA260Scale, the padding right of and below it is
// cleared, and only a successful luma pass scales the two half-size chroma
// planes. Byte-identical to Open-BFME-2's matched 0x001BAF30, ported from
// there; field names are structural.
extern "C" void *__cdecl memset(void *, int, unsigned int);
#pragma intrinsic(memset)

struct Rva009AA4F0PostProc
{
	unsigned char m_pad00[0x40];
	unsigned int m_frameWidth;
	unsigned char m_pad44[0x58 - 0x44];
	int m_hScale;
	int m_hRatio;
	int m_vScale;
	int m_vRatio;
	unsigned char m_pad68[0x70 - 0x68];
	unsigned int m_expandedWidth;
	unsigned int m_expandedHeight;
	int m_reconY;
	int m_reconU;
	int m_reconV;
	unsigned char m_pad84[0xB4 - 0x84];
	int m_border;
};

struct Rva009AA4F0Planes
{
	int m_yWidth;
	int m_yHeight;
	int m_yStride;
	int m_uvWidth;
	int m_uvHeight;
	int m_uvStride;
	unsigned char *m_y;
	unsigned char *m_u;
	unsigned char *m_v;
};

int __cdecl rva009AA4F0FrameScale(Rva009AA4F0PostProc *pp, unsigned char *frame,
	Rva009AA4F0Planes *config, int yOffset, int uvOffset)
{
	int destWidth = pp->m_expandedWidth;
	int hRatio = pp->m_hRatio;
	int vRatio = pp->m_vRatio;
	int vScale = pp->m_vScale;
	int hScale = pp->m_hScale;
	int sourceWidth = (pp->m_expandedWidth * hRatio + (hScale - 1)) / hScale;
	int destHeight = pp->m_expandedHeight;
	int sourceHeight = (pp->m_expandedHeight * vRatio + (vScale - 1)) / vScale;
	int paddedWidth;
	int paddedHeight;
	int result;
	int i;
	if (hRatio == 3)
		paddedWidth = (sourceWidth + 2) / 3 * 3 * pp->m_hScale / hRatio;
	else
		paddedWidth = (sourceWidth + 7) / 8 * 8 * pp->m_hScale / hRatio;
	if (vRatio == 3)
		paddedHeight = (sourceHeight + 2) / 3 * 3 * pp->m_vScale / vRatio;
	else
		paddedHeight = (sourceHeight + 7) / 8 * 8 * pp->m_vScale / vRatio;
	result = Rva009AA260Scale((Rva009AA260Context *)pp, frame + pp->m_reconY,
		pp->m_frameWidth + pp->m_border * 2, sourceWidth, sourceHeight,
		config->m_y + yOffset, config->m_yStride, destWidth, destHeight);
	for (i = 0; i < paddedHeight; i++)
		memset(config->m_y + i * config->m_yStride + destWidth + yOffset, 0,
			paddedWidth - destWidth);
	for (i = destHeight; i < paddedHeight; i++)
		memset(config->m_y + i * config->m_yStride + yOffset, 0, paddedWidth);
	if (result == 0)
		return 0;
	sourceWidth = (sourceWidth + 1) >> 1;
	sourceHeight = (sourceHeight + 1) >> 1;
	destWidth = (destWidth + 1) >> 1;
	destHeight = (destHeight + 1) >> 1;
	Rva009AA260Scale((Rva009AA260Context *)pp, frame + pp->m_reconU,
		(pp->m_frameWidth >> 1) + pp->m_border, sourceWidth, sourceHeight,
		config->m_u + uvOffset, config->m_uvStride, destWidth, destHeight);
	Rva009AA260Scale((Rva009AA260Context *)pp, frame + pp->m_reconV,
		(pp->m_frameWidth >> 1) + pp->m_border, sourceWidth, sourceHeight,
		config->m_v + uvOffset, config->m_uvStride, destWidth, destHeight);
	return result;
}
