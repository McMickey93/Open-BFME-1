// RVA 008A30C0: drain of the value registry that AptValue.cpp's slot-1
// release fills (g_rva01337810GcRoots: capacity +0, count +4, items +8).
// brief.py reports Libraries/Source/Apt/AptValue/AptValueVector.cpp as the
// EA source file. The caller ABI (registry pointer in ECX, no stack
// arguments, plain ret) comes from the matched callers in
// AptShutdown00894A90.cpp, AptGCShutdown.cpp and Rva008D19C0PopAfterStep.cpp.
//
// Every registered entry is popped. One whose twelve-bit reference count
// (bits 16..27) is non-zero again only loses its bit-30 "registered" mark;
// one still at zero is handed to vtable slot 2. The drain repeats until a
// pass finds the registry empty (presumably because slot-2 calls can
// register further values; that purpose is an inference).
//
// Retail keeps the outer pass loop unrotated (header test at +4, JMP back at
// +0x39) and loads the count into EAX before copying it to the pass counter.
// A while loop over an inlined pass that returns whether it found anything
// reproduces both; a plain nested while/do loop is rotated by the compiler.

class Rva00899560Value
{
public:
	virtual void addRef();
	virtual void release();
	virtual void idle();

	unsigned int m_flags;
};

struct Rva00899560Pool
{
	int m_capacity;
	int m_count;
	void **m_items;

	void rva008A30C0();

	__forceinline bool drainPass()
	{
		int count = m_count;
		if (count == 0)
			return false;
		for (int n = count; n; --n)
		{
			Rva00899560Value *value = (Rva00899560Value *)m_items[--m_count];
			unsigned int flags = value->m_flags;
			if ((flags & 0x0FFF0000) > 0)
				value->m_flags = flags & 0xBFFFFFFF;
			else
				value->idle();
		}
		return true;
	}
};

void Rva00899560Pool::rva008A30C0()
{
	while (drainPass())
		;
}
