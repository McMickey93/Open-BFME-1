// cl: /DNDEBUG /MD /EHsc
// Open-BFME5: clearRva00359330Nodes(Rva00359330Record *) -- retail 0x003593F0, 54 bytes.
//
// Drains the node chain hanging off a string record's +0x10 slot; the record
// layout is the one Rva00359330StringRecordRelease.cpp established (20-byte
// stride, name at +0x08). Retail reaches the existing 72-byte node destructor
// at 0x00354A00 through ILT 0x00042A32. Bind to its rowed Rva00354A00Node
// identity; this TU only reads the next-link prefix and never allocates or
// copies a node. The provider tears down the embedded subobject at +4.
// No named caller reaches this clearer (ILT 0x0001612B is unowned), so its
// function name remains address-derived.
//
// Shape lever (docs/shape_levers.md): the next link is read through the
// field, not the local, so VC7.1 keeps the delete null test after the store
// (retail test/store/branch). A do-while lands 51 B, a volatile reload 54 B
// with the test before the store.

void __cdecl operator delete(void *);

class Rva00354A00Node
{
public:
	~Rva00354A00Node();
	Rva00354A00Node *m_next;
};

struct Rva00359330Record
{
	int m_previous;
	int m_next;
	void *m_name;
	unsigned char m_released;
	unsigned char m_pad;
	unsigned short m_references;
	Rva00354A00Node *m_nodes;
};

// ?clearRva00359330Nodes@@YAXPAURva00359330Record@@@Z
void clearRva00359330Nodes(Rva00359330Record *record)
{
	while (record->m_nodes)
	{
		Rva00354A00Node *node = record->m_nodes;

		record->m_nodes = record->m_nodes->m_next;
		delete node;
	}
}

class BfmeNodeY
{
public:
	~BfmeNodeY();
	BfmeNodeY *m_next;
};

struct Rva00359530Record
{
	int m_previous;
	int m_next;
	void *m_name;
	unsigned char m_released;
	unsigned char m_pad;
	unsigned short m_references;
	BfmeNodeY *m_nodes;
};

// ?clearRva00359530Nodes@@YAXPAURva00359530Record@@@Z
void clearRva00359530Nodes(Rva00359530Record *record)
{
	while (record->m_nodes)
	{
		BfmeNodeY *node = record->m_nodes;

		record->m_nodes = record->m_nodes->m_next;
		delete node;
	}
}
