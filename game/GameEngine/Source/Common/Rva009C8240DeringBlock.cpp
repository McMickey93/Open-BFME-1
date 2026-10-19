// cl: /O2 /G6 /DNDEBUG /MD
// Retail 0x009C8240 (655 B), cdecl, no callers in retail: in-place adaptive
// smoothing of a width x height (at most 16 x 16) video block. The block's
// min and max pick a threshold from the 256-entry table at instance+0x453C
// (the larger of table[max] and table[255-min], plus (max-min)>>5); then a
// horizontal and a vertical pass replace each pixel by the rounded mean of
// itself twice and its two neighbours, a neighbour further than the threshold
// counting as the pixel itself. Each row or column is staged in a 16-byte
// buffer and written back whole.
// Byte-identical to Open-BFME-2's matched 0x001D8B40 (from its VP6 clean-room
// spec 001d8b40.md), ported from there; the volatile reads reproduce
// retail's load schedule. Address-derived name.
#include <stdlib.h>

extern "C" void * __cdecl memcpy(void *, const void *, unsigned int);
#pragma intrinsic(memcpy)

struct Rva009C8240Thresholds
{
	unsigned char m_unknown[0x453c];
	unsigned int m_threshold[256];
};

void __cdecl rva009C8240DeringBlock(void *instance, unsigned char *buffer,
	unsigned int stride, unsigned int width, unsigned int height)
{
	unsigned int x, y;
	unsigned char minimum = 255, maximum = 0;
	unsigned char *scan = buffer;
	unsigned int high;
	int threshold;
	unsigned char temp[16];
	const Rva009C8240Thresholds *context;
	int range;

	for (y = 0; y < height; ++y)
	{
		for (x = 0; x < width; ++x)
		{
			unsigned char pixel = *scan;
			if (pixel < minimum)
				minimum = pixel;
			if (pixel > maximum)
				maximum = pixel;
			++scan;
		}
		scan += stride - width;
	}
	context = (const Rva009C8240Thresholds *)instance;
	high = context->m_threshold[maximum];
	threshold = (int)context->m_threshold[255 - minimum];
	if ((unsigned int)threshold <= high)
		threshold = (int)high;
	range = maximum - minimum;
	unsigned int adjustment = (unsigned int)(range >> 5);
	threshold = (int)((unsigned int)*(volatile int *)&threshold + adjustment);

	instance = buffer;
	for (y = 0; y < height; ++y)
	{
		if (width > 0)
		{
			unsigned char *current = (unsigned char *)instance;
			for (x = 0; x < width; ++x)
			{
				int diffRight = abs(current[0] - current[1]);
				int diffLeft = abs(current[0] - current[-1]);
				int sum = 2 * (*(volatile unsigned char *)current);
				if (diffLeft <= threshold)
					sum += current[-1];
				else
					sum += current[0];
				if (diffRight <= threshold)
					sum += current[1];
				else
					sum += current[0];
				temp[x] = (unsigned char)((sum + 2) >> 2);
				++current;
			}
		}
		memcpy(instance, temp, width);
		instance = (unsigned char *)instance + stride;
	}
	for (x = 0; x < width; ++x)
	{
		unsigned char *above;
		unsigned char *below;
		unsigned char *destination;
		instance = buffer + x;
		above = (unsigned char *)instance - stride;
		below = (unsigned char *)instance + stride;
		for (y = 0; y < height; ++y)
		{
			int diffBottom = abs(*(unsigned char *)instance - *below);
			int diffTop = abs(*(unsigned char *)instance - *above);
			int sum = 2 * (*(unsigned char *)instance);
			if (diffTop <= threshold)
				sum += *above;
			else
				sum += *(unsigned char *)instance;
			if (diffBottom <= threshold)
				sum += *below;
			else
				sum += *(unsigned char *)instance;
			temp[y] = (unsigned char)((sum + 2) >> 2);
			above += stride;
			instance = (unsigned char *)instance + stride;
			below += stride;
		}
		destination = buffer + x;
		for (y = 0; y < height; ++y)
		{
			*destination = temp[y];
			destination += stride;
		}
	}
}
