// The body at retail RVA 0x003D0190 inserts a key when a five-argument search
// misses it.  The search helper is pinned as bfmeLowerRQ at ILT 0x00016B21.
// The vector insert helper is pinned as bfmeInsertRQ at ILT 0x00034D7E.
// No caller, vtable slot, or string identifies the owner.
// The class therefore keeps its address-derived name.

struct BfmeCmpRQ
{
	char m_bfmeRawRQ;
};

void ** __cdecl bfmeLowerRQ(void **begin, void **end, void **key, BfmeCmpRQ compare, int spare);

class BfmeVecRQ
{
public:
	void bfmeInsertRQ(void **where, void **key);

	void **m_bfmeBeginRQ;
	void **m_bfmeEndRQ;
};

// Matched Rva003D2B80Child::lookup takes this coordinate by value.  The user
// copy constructor and destructor reproduce retail's argument lowering at
// 0x003D01F0 (sub esp,8 copy plus the spilled temporary address); without
// them the body is 229 or 207 bytes instead of 237.
struct Rva003D2B80Coord
{
	float x;
	float y;

	Rva003D2B80Coord(const Rva003D2B80Coord &other) : x(other.x), y(other.y) {}
	~Rva003D2B80Coord() {}
};

struct Rva003D1380Elem
{
	unsigned char m_pad00[0x30];
	int m_count;
};

class Rva003D2B80Child
{
public:
	Rva003D1380Elem *lookup(Rva003D2B80Coord coord);
};

struct Rva003CDDB0Range
{
	const int *m_begin;
	const int *m_end;

	bool method(const Rva003CDDB0Range *other);
};

struct Rva003D01F0Template
{
	unsigned char m_pad00[0x08];
	Rva003CDDB0Range m_range;
	unsigned char m_pad10[0x1c - 0x10];
	unsigned short m_weight;
};

struct Rva003D01F0Anchor
{
	unsigned char m_pad00[0x38];
	Rva003D2B80Coord m_position;
};

struct Rva003D01F0Item
{
	void *m_vtable;
	Rva003D01F0Template *m_template;
	Rva003D01F0Anchor *m_anchor;
	unsigned char m_pad0c[0x24 - 0x0c];
	Rva003D2B80Coord m_position;
};

class Rva003D0190
{
public:
	void ensure(void *key);
	void method003D01F0(Rva003D01F0Item *item);
	void method003D0320(Rva003D01F0Item *item);
	void method003D0440(Rva003D01F0Item *item);

	Rva003CDDB0Range m_range;
	unsigned char m_pad08[0x10 - 0x08];
	Rva003D2B80Child *m_children[4];
	unsigned char m_pad20[0x30 - 0x20];
	BfmeVecRQ m_bfmeVecRQ;
};

void Rva003D0190::ensure(void *key)
{
	void **end = m_bfmeVecRQ.m_bfmeEndRQ;
	BfmeCmpRQ compare;
	compare.m_bfmeRawRQ = 0;
	void **found = bfmeLowerRQ(m_bfmeVecRQ.m_bfmeBeginRQ,
		end, &key, compare, 0);

	if (found == end || *found != key)
		m_bfmeVecRQ.bfmeInsertRQ(found, &key);
}

// Retail 0x003D01F0 (ret 4, 237 bytes) passes its own this to
// Rva003D0190::ensure and Rva003CDDB0Range::method, and walks the four child
// lookups at +0x10.  No caller names the method, so it keeps its address.
void Rva003D0190::method003D01F0(Rva003D01F0Item *item)
{
	if (!m_range.method(&item->m_template->m_range))
		return;

	Rva003D2B80Coord newPosition = item->m_position;
	Rva003D2B80Coord oldPosition = item->m_anchor->m_position;
	for (int i = 0; i < 4; ++i)
	{
		if (m_children[i] == 0)
			continue;
		Rva003D1380Elem *from = m_children[i]->lookup(newPosition);
		Rva003D1380Elem *to = m_children[i]->lookup(oldPosition);
		if (from == to)
			continue;
		if (from != 0)
		{
			from->m_count -= item->m_template->m_weight;
			if (from->m_count < 0)
				from->m_count = 0;
			ensure(from);
		}
		if (to != 0)
		{
			to->m_count += item->m_template->m_weight;
			ensure(to);
		}
	}
}

// Retail 0x003D0320 (ret 4, 227 bytes) and 0x003D0440 (ret 4, 224 bytes) are
// the add and remove counterparts of 0x003D01F0: one child lookup per child,
// with the sorted insert written out inline.  Comparing the found entry
// against the element rather than the address-taken key is what lets retail
// keep the element in ESI; Rva003D0190::ensure's own form does not.
void Rva003D0190::method003D0320(Rva003D01F0Item *item)
{
	if (!m_range.method(&item->m_template->m_range))
		return;

	Rva003D2B80Coord position = item->m_anchor->m_position;
	for (int i = 0; i < 4; ++i)
	{
		if (m_children[i] == 0)
			continue;
		Rva003D1380Elem *elem = m_children[i]->lookup(position);
		if (elem == 0)
			continue;
		elem->m_count += item->m_template->m_weight;

		{
			void *key = elem;
			void **end = m_bfmeVecRQ.m_bfmeEndRQ;
			BfmeCmpRQ compare;
			compare.m_bfmeRawRQ = 0;
			void **found = bfmeLowerRQ(m_bfmeVecRQ.m_bfmeBeginRQ,
				end, &key, compare, 0);
			if (found == end || *found != elem)
				m_bfmeVecRQ.bfmeInsertRQ(found, &key);
		}
	}
}

void Rva003D0190::method003D0440(Rva003D01F0Item *item)
{
	if (!m_range.method(&item->m_template->m_range))
		return;

	Rva003D2B80Coord position = item->m_position;
	for (int i = 0; i < 4; ++i)
	{
		if (m_children[i] == 0)
			continue;
		Rva003D1380Elem *elem = m_children[i]->lookup(position);
		if (elem == 0)
			continue;
		elem->m_count -= item->m_template->m_weight;
		if (elem->m_count < 0)
			elem->m_count = 0;

		{
			void *key = elem;
			void **end = m_bfmeVecRQ.m_bfmeEndRQ;
			BfmeCmpRQ compare;
			compare.m_bfmeRawRQ = 0;
			void **found = bfmeLowerRQ(m_bfmeVecRQ.m_bfmeBeginRQ,
				end, &key, compare, 0);
			if (found == end || *found != elem)
				m_bfmeVecRQ.bfmeInsertRQ(found, &key);
		}
	}
}
