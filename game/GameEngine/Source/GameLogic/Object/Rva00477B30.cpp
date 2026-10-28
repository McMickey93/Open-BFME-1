// cl: /DNDEBUG /MD /EHsc
// Open-BFME: retail 0x00477B30 (7 B), a dead getter returning the pointer
// at this+0x19C. Its ILT jmp 0x00002784 has no callers. Retail's ILT order
// rules out Object::getAI here (the oracle confirms that name at 0x000E59A0,
// the +0x204 getter BFME's matched Object users inline), so class and method
// keep the address.

class Rva00477B30Value;

class Rva00477B30
{
public:
	Rva00477B30Value *get();

private:
	unsigned char m_pad000[0x19c];
	Rva00477B30Value *m_value;
};

Rva00477B30Value *Rva00477B30::get()
{
	return m_value;
}
