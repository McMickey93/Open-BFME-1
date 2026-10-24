// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// Retail 0x008C66A0 (129 bytes, RET at +0x7A and +0x80). Address-owned Apt
// callback: it reads the integer on the Apt stack top, and when that slot of
// the holder's 32-byte value-stack table is live, releases its +4 value,
// clears it, releases the whole stack and drops the live-slot count at
// holder+0x1234. Its registered name and semantic identity are unknown.

class AptValue
{
public:
	int toInteger() const;
	bool isUndefined() const { return ((m_valueBits >> 15) & 1) == 0; }

private:
	void *m_vtable;
	unsigned int m_valueBits;
};

class Rva008A0FF0Value
{
public:
	virtual void slot00();
	virtual void release();
};

class Rva008A0FF0ValueStack
{
public:
	void releaseAll();

	void *m_value00;
	Rva008A0FF0Value *m_value04;
	int m_value08;
	int m_value0C;
	int m_value10;
	int m_count;
	int m_capacity;
	Rva008A0FF0Value **m_values;
};

struct Rva008AE770Stack
{
	int m_count;
	int m_rva0133874C;
	AptValue **m_rva01338750;
};

extern Rva008AE770Stack Rva008AE770TheStack;
extern AptValue **g_bfmeArr1233;
extern AptValue *g_bfmeFallbackDB;
extern char *Rva008A5380Holder;

AptValue *__cdecl dup_008c66a0()
{
	AptValue *arg = g_bfmeArr1233[Rva008AE770TheStack.m_count - 1];
	if (!arg->isUndefined())
	{
		int index = arg->toInteger();
		char *holder = Rva008A5380Holder;
		if (((Rva008A0FF0ValueStack *)*(char **)(holder + 0x1230))[index].m_value00)
		{
			((Rva008A0FF0ValueStack *)*(char **)(holder + 0x1230))[index].m_value04->release();
			((Rva008A0FF0ValueStack *)*(char **)(Rva008A5380Holder + 0x1230))[index].m_value00 = 0;
			((Rva008A0FF0ValueStack *)*(char **)(Rva008A5380Holder + 0x1230))[index].releaseAll();
			--*(int *)(Rva008A5380Holder + 0x1234);
		}
	}
	return g_bfmeFallbackDB;
}
