// cl: /DNDEBUG /DWIN32 /MD /D_STLP_USE_STATIC_LIB
// stlport
// GameState::addPostProcessSnapshot, retail 0x0010FE90, 204 bytes. EA's
// WorldBuilder labels name it; the callback at 0x00110790 proves the receiver
// and two-argument thiscall ABI, and the ILT slot fits (Snapshot *, unsigned).
// Open-BFME-2's twin (0x002DCF6C) reads the second argument as a load
// sequence number stored beside each snapshot.
#define _STLP_NO_EXCEPTIONS 1
#include <list>
#include <string.h>

struct Rva0010EBE0Element
{
	int m_body;
	Rva0010EBE0Element(void *body) : m_body((int)body) {}
};

class Snapshot;

struct Rva0010ECA0Elem
{
	Snapshot *m_snapshot;
	unsigned int m_sequence;
};

// Keep STLport's real push_front visible, but out of line as in retail.
// Its 47 bytes also match 0x0010EBE0. Visibility proves that it copies the
// argument without retaining its address, preserving the caller's arg home.
template <> __declspec(noinline)
void _STL::list<Rva0010EBE0Element, _STL::allocator<Rva0010EBE0Element> >::push_front(
	const Rva0010EBE0Element &value)
{
	insert(begin(), value);
}

class Rva0010ECA0List
{
public:
	void push_back(Rva0010ECA0Elem const &value);
	_STL::list<Rva0010ECA0Elem> m_list;
};

class Rva0010FE90Named
{
public:
	virtual void v00();
	virtual void v04();
	virtual const char *name();
};

class GameState
{
public:
	void addPostProcessSnapshot(Snapshot *snapshot, unsigned int sequence);
private:
	unsigned char m_unmodelled_00[0x48];
	_STL::list<Rva0010EBE0Element> m_items; // +0x48
	Rva0010ECA0List m_pairs;               // +0x4C
};

void GameState::addPostProcessSnapshot(Snapshot *snapshot, unsigned int sequence)
{
	if (snapshot == 0)
		return;

	const char *name = ((Rva0010FE90Named *)snapshot)->name();
	if (name != 0)
	{
		if (strcmp(name, "Object") == 0)
		{
			// Retail passes the address of the original four-byte argument.
			m_items.push_front(reinterpret_cast<const Rva0010EBE0Element &>(snapshot));
			Rva0010ECA0Elem pair;
			pair.m_snapshot = snapshot;
			pair.m_sequence = sequence;
			m_pairs.push_back(pair);
			return;
		}
		if (strcmp(name, "Weapon") == 0)
			return;
	}

	m_items.push_back(Rva0010EBE0Element(snapshot));
	Rva0010ECA0Elem pair;
	pair.m_snapshot = snapshot;
	pair.m_sequence = sequence;
	m_pairs.m_list.push_back(pair);
}
