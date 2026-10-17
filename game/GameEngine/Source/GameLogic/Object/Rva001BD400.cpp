// cl: /DNDEBUG /MD /EHsc
// Open-BFME: retail 0x001BD400 (15 B), a dead const getter that copies the
// 4-byte value at this+0x1A4 into a hidden return slot (so the value type has a
// constructor). Its ILT jmp 0x00023907 has no callers, and retail's ILT order
// rules out Object::getDisabledFlags, so class and method keep the address.

class Rva001BD400Value
{
public:
	Rva001BD400Value() : m_bits(0) {}

	unsigned int m_bits;
};

class Rva001BD400
{
public:
	Rva001BD400Value get() const;

private:
	unsigned char m_pad000[0x1a4];
	Rva001BD400Value m_value;
};

Rva001BD400Value Rva001BD400::get() const
{
	return m_value;
}
