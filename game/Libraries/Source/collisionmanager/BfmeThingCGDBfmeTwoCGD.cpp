// BFME 1 0x009A30B0 (333 bytes): BfmeThingCGD::bfmeTwoCGD, the contact pass of
// the collision manager. The matched bfmeGoCGD (0x009A4A30) calls this method
// on the same object, and the BFME 1 class layout has the contact bucket array
// at +0xAE10, the active cursor at +0xC05C, the index at +0xC060 and the
// current cursor at +0xC064, matching the donor's CollisionManagerImpl.
//
// Source: BFME 2 donor Code/Libraries/Source/collisionmanager/collisionmanager_impl.cpp,
// CollisionManagerImpl::bfmeTwoCGD (donor revision ce1b975697c2f20e514174e3875f8820d1dba612),
// whose compiled body is exact against this address. This TU keeps the BFME 1
// names for the fields this pass uses, at the same offsets, with the donor's
// contact-node view; the opaque prefix is a single padding member.
// The reverse-normal copy is written as explicit float copies followed by
// negation: the canonical Coord3D is POD, and this spelling reproduces the
// donor user-copy-constructor codegen (x87 copy of x and y, integer z) that a
// bitwise POD copy does not.
#include "../../Include/Lib/Coord3D.h"

struct Rva009A30B0Object;

// Virtual interface at the contact data's +4 source pointer. Slot roles follow
// the donor's ABI evidence: primaryObject is slot 0x0C; the test at 0x20 and
// the response at 0x24 are three-argument callbacks (RET 12). The location and
// normal belong to the outer callback, not to the getter.
struct Rva009A30B0Source
{
	virtual void slot00() = 0;
	virtual void slot04() = 0;
	virtual void slot08() = 0;
	virtual Rva009A30B0Object *primaryObject() const = 0;
	virtual void slot10() = 0;
	virtual void slot14() = 0;
	virtual void slot18() = 0;
	virtual void slot1C() = 0;
	virtual bool test(const Rva009A30B0Object *, const Coord3D &, const Coord3D &) const = 0;
	virtual void respond(Rva009A30B0Object *, const Coord3D &, const Coord3D &) = 0;
};

struct Rva009A30B0Data
{
	void *m_owner;				// +0x00
	Rva009A30B0Source *m_source;		// +0x04
};

struct Rva009A30B0Node
{
	Rva009A30B0Data *first;			// +0x00
	Rva009A30B0Data *second;		// +0x04
	unsigned int key0;			// +0x08
	unsigned int key1;			// +0x0C
	unsigned int state;			// +0x10
	Coord3D point;				// +0x14
	Coord3D normal;				// +0x20
	Rva009A30B0Node **back;			// +0x2C
	Rva009A30B0Node *next;			// +0x30
};

struct Rva009A30B0ReverseNormal
{
	Coord3D value;
	Rva009A30B0ReverseNormal(const Coord3D &normal)
	{
		value.x = normal.x;
		value.y = normal.y;
		value.z = normal.z;
		value.x = -value.x;
		value.y = -value.y;
		value.z = -value.z;
	}
	operator const Coord3D &() const { return value; }
};

// TU-local view of BfmeThingCGD covering only the fields the contact pass
// reads and writes at their BFME 1 offsets. The pointee type is the contact
// node rather than Rva009A2FE0Node; the bucket slots and cursors are the same
// pointers at the same addresses (BfmeConv597.cpp's hash-chain view).
class BfmeThingCGD
{
public:
	void bfmeTwoCGD();
	char pad00[0xAE10];			// +0x0000
	Rva009A30B0Node *m_buckets[0x493];	// +0xAE10
	Rva009A30B0Node *m_active;		// +0xC05C
	int m_index;				// +0xC060
	Rva009A30B0Node *m_cur;			// +0xC064
};

void BfmeThingCGD::bfmeTwoCGD()
{
	m_index = 0;
	m_cur = m_buckets[0];
	for (;;)
	{
		while (m_cur == 0)
		{
			int i = m_index + 1;
			if (i == 0x493)
				return;
			m_index = i;
			m_cur = m_buckets[i];
		}
		Rva009A30B0Node *node = m_cur;
		m_cur = m_cur->next;
		if (node == 0)
			return;
		if (node->first->m_source == 0 || node->second->m_source == 0)
			continue;
		if (node->state == 0)
			node->state = node->first->m_source->test(
				node->second->m_source->primaryObject(), node->point, node->normal) ? 1 : 2;
		if (node->state == 2)
			continue;
		node->first->m_source->respond(
			node->second->m_source->primaryObject(), node->point, node->normal);
		if (node->first->m_source == 0 || node->second->m_source == 0)
			continue;
		node->second->m_source->respond(node->first->m_source->primaryObject(),
			node->point, Rva009A30B0ReverseNormal(node->normal));
	}
}
