// ?rva008B9080ShiftCache@@YAPAXPAURva008B9020Owner@@@Z
// partial score=0.8972 date=2026-10-17
// Sibling of the matched pop-back 0x008B9020 (game/Libraries/Source/EA/Apt/Rva008B9020PopCache.cpp):
// land it there, after that body, sharing Rva008B9020Owner.
class AptValue;
extern AptValue *g_bfmeFallbackDB;
struct Rva008B9020Owner
{
	unsigned char m_pad0[4];
	unsigned int m_flags;
	unsigned char m_pad1[0x20 - 8];
	void **m_arr;
	unsigned char m_pad2[4];
	int m_count;
};

// 0x008B9080: shift the front entry off the same tagged array, falling back to
// the Apt null value.
extern "C" void *__cdecl memmove(void *dst, const void *src, unsigned int size);

void *rva008B9080ShiftCache(Rva008B9020Owner *obj)
{
	void *fallback = g_bfmeFallbackDB;
	unsigned int flags = obj->m_flags;
	if ((flags & 0x3f) == 0x16)
	{
		unsigned char bit = (unsigned char)(flags >> 15);
		bit = ~bit;
		if (bit & 1)
			return fallback;
		int count = obj->m_count;
		if (count <= 0)
			return fallback;
		unsigned int masked = (unsigned int)obj->m_arr[0] & ~1u;
		void *result = masked ? (void *)masked : fallback;
		int newCount = count - 1;
		int *countPtr = &obj->m_count;
		*countPtr = newCount;
		if (newCount != 0)
			memmove(obj->m_arr, obj->m_arr + 1, newCount * sizeof(void *));
		obj->m_arr[obj->m_count] = 0;
		return result;
	}
	return fallback;
}
