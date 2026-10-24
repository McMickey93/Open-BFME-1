// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
//
// The constructor stores vtable 0x01136AF8 after calling Rva00899F00Base's
// constructor at 0x00899F00.  The address-derived type name reflects that
// the retail binary does not expose a trusted public class name.

// Retail table at VA 0x01136AF8: 19 slots, ending before 0x01136B44.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?bfmeBump@Gen_008991B0@@QAEXXZ")();
extern "C" void __identifier("?release@Rva00899560Value@@UAEXXZ")();
extern "C" void __identifier("?invoke@Rva00891810Object@@QAEXXZ")();
extern "C" void __identifier("?bfmeTotal899410@BfmeThing899410@@QBEHXZ")();
extern "C" void __identifier("?bfmeSub1224@BfmeA1224@@QAEPAVBfmeE1224@@H@Z")();
extern "C" void __identifier("?value@Rva00899480True@@QBE_NXZ")();
extern "C" void __identifier("?field@Rva00899490FieldAddress@@QAEPAHXZ")();
extern "C" void __identifier("?getBit8@Rva008993E0Owner@@QAEHXZ")();
extern "C" void __identifier("?setBit8@Rva008993E0Owner@@QAEXH@Z")();
extern "C" void __identifier("?value@Rva008994A0True@@QBE_NXZ")();
extern "C" void __identifier("?Rva008B5940Lookup@@YGPAVBfmeS1083@@PAXPBUString008B5940@@@Z")();
extern "C" void __identifier("?dup_00891890@@YAXXZ")();
extern "C" void __identifier("?apply@Rva008918A0@@QAEXXZ")();
extern "C" void __identifier("??_GRva008B58B0HeaderedDeleting@@UAEPAXI@Z")();
extern "C" void __identifier("?Rva008918B0Noop@@YAXXZ")();
extern "C" void __identifier("?process@Rva00899460Object@@QAEXXZ")();
extern "C" void __identifier("?notify@Q4Base00D35D68@@QAEXHH@Z")();
extern "C" void __identifier("?copyLowByte@Rva008994B0@@QAEIPAI@Z")();
extern "C" void __identifier("?contains@Rva008994D0@@QAE_NPAI@Z")();
extern "C" void *bfmeVft008B5880[] = {
    reinterpret_cast<void *>(&__identifier("?bfmeBump@Gen_008991B0@@QAEXXZ")),
    reinterpret_cast<void *>(&__identifier("?release@Rva00899560Value@@UAEXXZ")),
    reinterpret_cast<void *>(&__identifier("?invoke@Rva00891810Object@@QAEXXZ")),
    reinterpret_cast<void *>(&__identifier("?bfmeTotal899410@BfmeThing899410@@QBEHXZ")),
    reinterpret_cast<void *>(&__identifier("?bfmeSub1224@BfmeA1224@@QAEPAVBfmeE1224@@H@Z")),
    reinterpret_cast<void *>(&__identifier("?value@Rva00899480True@@QBE_NXZ")),
    reinterpret_cast<void *>(&__identifier("?field@Rva00899490FieldAddress@@QAEPAHXZ")),
    reinterpret_cast<void *>(&__identifier("?getBit8@Rva008993E0Owner@@QAEHXZ")),
    reinterpret_cast<void *>(&__identifier("?setBit8@Rva008993E0Owner@@QAEXH@Z")),
    reinterpret_cast<void *>(&__identifier("?value@Rva008994A0True@@QBE_NXZ")),
    reinterpret_cast<void *>(&__identifier("?Rva008B5940Lookup@@YGPAVBfmeS1083@@PAXPBUString008B5940@@@Z")),
    reinterpret_cast<void *>(&__identifier("?dup_00891890@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?apply@Rva008918A0@@QAEXXZ")),
    reinterpret_cast<void *>(&__identifier("??_GRva008B58B0HeaderedDeleting@@UAEPAXI@Z")),
    reinterpret_cast<void *>(&__identifier("?Rva008918B0Noop@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?process@Rva00899460Object@@QAEXXZ")),
    reinterpret_cast<void *>(&__identifier("?notify@Q4Base00D35D68@@QAEXHH@Z")),
    reinterpret_cast<void *>(&__identifier("?copyLowByte@Rva008994B0@@QAEIPAI@Z")),
    reinterpret_cast<void *>(&__identifier("?contains@Rva008994D0@@QAE_NPAI@Z")),
};

struct Rva008B5880Inner
{
	char m_pad[4];
	void *m_04;
};

struct Rva008B5880Mid
{
	char m_pad[0x0c];
	Rva008B5880Inner *m_0c;
};

struct Rva008B5880Arg
{
	char m_pad[0x50];
	Rva008B5880Mid *m_50;
};

class Rva00899F00Base
{
public:
	Rva00899F00Base(unsigned int argument0, int argument1);
};

class Rva008B5880 : public Rva00899F00Base
{
public:
	Rva008B5880(Rva008B5880Arg *arg);

	int *m_vfptr;
	char m_pad04[0x1c];
	void *m_20;
	void *m_24;
	void *m_28;
};

Rva008B5880::Rva008B5880(Rva008B5880Arg *arg) :
	Rva00899F00Base(0x15, 8)
{
	Rva008B5880Arg *p = arg;
	m_24 = reinterpret_cast<void *>(0);
	m_vfptr = reinterpret_cast<int *>(bfmeVft008B5880);
	int z = 0;
	void *v = p->m_50->m_0c->m_04;
	m_20 = v;
	m_28 = reinterpret_cast<void *>(z);
}
