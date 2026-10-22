// ?rva004533f0@@YA_NPBURva004533F0Record@@0@Z
// partial score=0.7739 date=2026-10-22
// cl: /DNDEBUG /MD
struct Rva004533F0TreeNode
{
	unsigned char m_pad[8];
	Rva004533F0TreeNode *m_payload;
};

// ILT 0x000162E8 jumps to 0x008525B0, the matched _STL::equal
// instantiation over three Rb-tree iterator values.
extern "C" bool __cdecl __identifier("?j_000162e8@@YAXXZ")(
	Rva004533F0TreeNode *first, Rva004533F0TreeNode *last,
	Rva004533F0TreeNode *second);

struct Rva004533F0Record
{
	unsigned char m_byte0, m_byte1, m_byte2, m_pad3;
	int m_word4;
	Rva004533F0TreeNode *m_item8;
	int m_serialC;
	int m_unused10;
};

bool __cdecl rva004533f0(const Rva004533F0Record *first,
	const Rva004533F0Record *second)
{
	const Rva004533F0Record *a = first;
	const Rva004533F0Record *b = second;
	for (int i = 0; i < 8; ++i, ++a, ++b)
	{
		if (a->m_byte0 != b->m_byte0 || a->m_byte1 != b->m_byte1 ||
			a->m_byte2 != b->m_byte2 || a->m_word4 != b->m_word4 ||
			a->m_serialC != b->m_serialC)
			return 0;
		Rva004533F0TreeNode *item = a->m_item8;
		if (!__identifier("?j_000162e8@@YAXXZ")(
			item->m_payload, item, b->m_item8->m_payload))
			return 0;
	}
	return 1;
}
