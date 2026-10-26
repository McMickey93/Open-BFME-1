// cl: /O2 /Ob0

struct Rva00926720Key
{
	unsigned low;
	unsigned high;
};
class Rva00926720ModuloIndex
{
	void *m_reserved;
	unsigned *m_begin;
	unsigned *m_end;
public:
	unsigned index(const Rva00926720Key *key) const;
};
unsigned Rva00926720ModuloIndex::index(const Rva00926720Key *key) const
{
	unsigned count = m_end - m_begin;
	return ((key->high << 16) + key->low) % count;
}

// Retail 0x00926770 (unreferenced, after int3 padding, two rows on): the
// matching key comparison of the same hash traits, thiscall with `this`
// unused and ret 8 -- both halves must agree. Address-derived name.
class Rva00926770KeyEqual
{
public:
	int equal(const Rva00926720Key *a, const Rva00926720Key *b) const;
};
int Rva00926770KeyEqual::equal(const Rva00926720Key *a, const Rva00926720Key *b) const
{
	if (a->low == b->low && a->high == b->high)
		return 1;
	return 0;
}
