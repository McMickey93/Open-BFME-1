// cl: /DNDEBUG /MD /EHsc
// stlport
#include <vector>

class BFMERetailAsciiString
{
public:
	BFMERetailAsciiString(const char *text);
	~BFMERetailAsciiString();
	void *m_buffer;
};

class Rva00387D90String : public BFMERetailAsciiString
{
public:
	Rva00387D90String(const char *text) : BFMERetailAsciiString(text) {}
};

class Rva00387D90Owner
{
public:
	Rva00387D90String *at(int index);
	unsigned char m_head[0x54];
	std::vector<Rva00387D90String> m_slots;
};

Rva00387D90String *Rva00387D90Owner::at(int index)
{
	if (index >= 0 && (unsigned int)index < (unsigned int)m_slots.size())
		return &m_slots[index];
	// The fallback is the plain string: its atexit teardown (0x00C6FE60)
	// jumps straight to the string destructor ILT 0x0000D828.
	static BFMERetailAsciiString invalid("Invalid Slot");
	return (Rva00387D90String *)&invalid;
}
