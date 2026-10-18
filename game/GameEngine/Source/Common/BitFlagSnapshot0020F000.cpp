// cl: /Iinputs/reference/shims/zhcanonascii /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include
// stlport
struct FlagVersion0020F000
{
	unsigned char data[2];
	unsigned char padding[2];
};

struct FlagError0020F000
{
	char *text;
	int tag;
};

#define __PLACEMENT_VEC_NEW_INLINE
#include "ascii_string.h"

class XferException
{
public:
	XferException(int tag, const char *format, ...);
	XferException(const XferException &that);
	~XferException(void);
	char *text;
	int tag;
};

class FlagXfer0020F000
{
public:
	virtual void slot00();
	virtual bool IsLoading();
	virtual bool IsStoring();
	virtual bool IsCRC();
	virtual bool IsLightCRC();
	virtual void slot05();
	virtual void slot06();
	virtual void slot07();
	virtual void slot08();
	virtual FlagXfer0020F000 &xferUser(void *, unsigned int);
	virtual FlagXfer0020F000 &xferVersion(FlagVersion0020F000 &);
	virtual void slot11();
	virtual void xferSnapshot(void *);
	virtual void slot13();
	virtual void slot14();
	virtual void slot15();
	virtual void slot16();
	virtual void slot17();
	virtual void slot18();
	virtual void slot19();
	virtual void slot20();
	virtual void slot21();
	virtual void slot22();
	virtual void slot23();
	virtual void slot24();
	virtual void slot25();
	virtual FlagXfer0020F000 &xferAsciiString(AsciiString &);
	virtual void slot27();
	virtual void slot28();
	virtual FlagXfer0020F000 &xferUnsignedInt(unsigned int &);
	virtual FlagXfer0020F000 &xferInt(int &);
	virtual FlagXfer0020F000 &xferUnsignedShort(unsigned short &);
	virtual void slot32();
	virtual void slot33();
	virtual void slot34();
	virtual FlagXfer0020F000 &xferBool(bool &);
};

class Xfer;

class PackedFlags0020ECA0
{
public:
	void xfer(Xfer *xfer);
};

#include <bitset>
#include "Common/BitFlags.h"
int __cdecl bfmeLookupC(void *name);

class BitFlagSnapshot0020F000
{
public:
	void xfer(FlagXfer0020F000 *xfer);

	unsigned int bits;
};

// ?xfer@BitFlagSnapshot0020F000@@QAEXPAVFlagXfer0020F000@@@Z
void BitFlagSnapshot0020F000::xfer(FlagXfer0020F000 *xfer)
{
	FlagVersion0020F000 version;
	version.data[0] = 1;
	version.data[1] = 1;
	xfer->xferVersion(version);
	if (xfer->IsLightCRC())
	{
		reinterpret_cast<PackedFlags0020ECA0 *>(this)->xfer(reinterpret_cast<Xfer *>(xfer));
		return;
	}

	if (xfer->IsStoring())
	{
		const unsigned char *cursor = reinterpret_cast<const unsigned char *>(this);
		const unsigned char *end = cursor + 4;
		int total = 0;
		while (cursor < end)
		{
			total += _STL::_Bs_G<bool>::_S_bit_count[*cursor];
			++cursor;
		}
		int checksum = total;
		xfer->xferInt(checksum);

		for (int bit = 0; bit < 11; ++bit)
		{
			if ((bits & (1 << (bit & 31))) != 0)
			{
				const char *name = BitFlags<11>::getBitNames()[bit];
				if (name != 0)
				{
					AsciiString string(name);
					xfer->xferAsciiString(reinterpret_cast<AsciiString &>(string));
					--checksum;
				}
			}
		}
	}
	else
	{
		bits = 0;
		int count;
		xfer->xferInt(count);
		AsciiString string;
		for (int bit = 0; bit < count; ++bit)
		{
			xfer->xferAsciiString(reinterpret_cast<AsciiString &>(string));
			int flag = bfmeLookupC((void*)string.str());
			if (flag < 0)
			{
				throw XferException(0, 0);
			}
			bits |= 1 << (flag & 31);
		}
	}
}

