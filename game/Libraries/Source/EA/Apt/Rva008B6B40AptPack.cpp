// ?aptWeekday30At008B6B40@@YAPAVAptInteger@@PAXH@Z
// ?aptThirdLo@@YAPAVAptValue@@PAURva008B6B40Self@@H@Z
// cl: /DNDEBUG /MD /EHsc
class AptValue;
class AptInteger { public: static AptInteger* Create(int value); };
// Opaque receiver of the matched weekday helper at 0x008B66B0; the matched
// caller 0x008B6880 passes its fields +0x38, +0x34 and +0x30 the same way.
class Rva008B6880 {
public:
	int rva008B66B0(int, int, int);
	unsigned char m_unknown00[0x30];
	int m_unknown30, m_unknown34, m_unknown38;
};
// RVA 0x008B6B40: weekday of the fields at +0x30..+0x38 as an Apt integer.
AptInteger *aptWeekday30At008B6B40(void *self, int argc)
{
	Rva008B6880 *date = (Rva008B6880 *)self;
	return AptInteger::Create(date->rva008B66B0(date->m_unknown38, date->m_unknown34, date->m_unknown30));
}
struct Rva008B6B40Self { char m_pad[0x30]; int m_a; int m_b; int m_c; };
AptValue* aptThirdLo(Rva008B6B40Self* self, int argc)
{
	return (AptValue*)AptInteger::Create(self->m_c);
}
