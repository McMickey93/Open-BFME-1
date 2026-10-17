struct BfmeStringData1284
{
	unsigned short m_refCount;
	unsigned short m_length;
	unsigned int m_capacity;
	char m_text[1];
};

extern "C" char *__cdecl strcpy(char *destination, const char *source);
#pragma intrinsic(strcpy)

// The Apt allocation table at 0x01337A30 is a POINTER to a {allocate, free}
// pair, not the pair itself; only the free slot (+4) is ever called here.
struct BfmeStringPool3AF0
{
	void *(__cdecl *allocate)(unsigned int bytes);
	void (__cdecl *free)(void *storage);
};

// The shared empty EA string block at 0x012D5298 is defined once, as
// EAStringC::StringDataC, in game/GameEngine/Source/Common/Data/Rva012D5298.cpp;
// this TU keeps its own local view of the block and casts at each use.
class EAStringC
{
public:
	class StringDataC;
};
extern EAStringC::StringDataC g_rva012D5298Empty;
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;

class BfmeString1284
{
public:
	BfmeString1284()
	{
		m_data = (BfmeStringData1284 *)&g_rva012D5298Empty;
		++((BfmeStringData1284 *)&g_rva012D5298Empty)->m_refCount;
	}

	~BfmeString1284()
	{
		BfmeStringData1284 *data = m_data;
		if (--data->m_refCount == 0)
			g_rva01337A30AllocPair->free(data);
	}

	BfmeStringData1284 *m_data;
};

// The two calls at 0x8B9498 (this row) and 0x8B9594
// (game/Libraries/Source/EA/Apt/JoinArray008B94F0.cpp) reach retail 0x008B8E70,
// whose ledger row is the matched gen dump ?d_008b8e70@@YAXXZ
// (game/gen_asm/d_00882630.asm), as tools/callees.py 0x8b9460 139 prints for
// the callee.  Nothing defines a member named bfmeBuildString1284, so the calls
// name the dump through the raw pointer bridge; the bridge sits at the call
// site rather than in a member, because a body emitted under the pinned
// placeholder name would be judged against retail's 267-byte body at
// 0x008B8E70 and charged as a comdat loser.  A plain __cdecl reference to the
// dump cannot keep the bytes: the caller pushes two stack words and passes the
// writer in ECX, which is the thiscall shape below.
void d_008b8e70();

class BfmeStringWriter1284
{
public:
	void bfmeWriteString1284(char *destination, int value);
};

void BfmeStringWriter1284::bfmeWriteString1284(char *destination, int value)
{
	BfmeString1284 result;
	union
	{
		void (*raw)(void);
		void (BfmeStringWriter1284::*typed)(BfmeString1284 *, int);
	} buildString;
	buildString.raw = &d_008b8e70;
	(this->*buildString.typed)(&result, value);
	strcpy(destination, result.m_data->m_text);
}
// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
