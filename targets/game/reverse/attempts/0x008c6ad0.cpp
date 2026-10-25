// ?BooleanCoerce008C6AD0@@YAPAVAptValue@@PAXH@Z
// partial score=0.4506 date=2026-10-25
// ?rva8CF1B0ProcessRecord@@YAXPAVRva8CF1B0State@@PAURva8CF1B0Cursor@@@Z
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc

struct Rva8CF1B0StringBlock { unsigned short m_refs; };

// The Apt allocator-hook pair pointer at VA 0x01337A30, defined once by
// game/Libraries/Source/Apt/Apt.cpp.  Slot +4 is the deallocator this TU calls;
// the view below is the TU-local spelling of that second slot.
struct BfmeStringPool3AF0;
extern struct BfmeStringPool3AF0 *g_rva01337A30AllocPair;

struct Rva01337A30PoolView
{
	void *m_alloc;
	void (__cdecl *m_free)(void *storage);
};

class BfmeStrVKI
{
public:
	BfmeStrVKI(const char *text) { bfmeSetVKI(text); }
	~BfmeStrVKI()
	{
		Rva8CF1B0StringBlock *block = m_block;
		--block->m_refs;
		if (block->m_refs == 0)
			((Rva01337A30PoolView *)g_rva01337A30AllocPair)->m_free(block);
	}
	void bfmeSetVKI(const char *text);
private:
	Rva8CF1B0StringBlock *m_block;
};

class Rva8CF1B0Value
{
public:
	virtual void addRef();
	virtual void release();
	unsigned m_flags;
};

// Retail 0x008CCED0 is the matched Rva008CCED0BytecodeRunner::run (Rva008CCED0BytecodeRunner.cpp).
class Rva008CCED0BytecodeRunner { public: unsigned char *run(void *, void *, int); };
class BfmeR1226
{
public:
};

class Rva8CD130String;
class Rva8CD130Value;
// 0x008CC690 has no converted body yet: symbols.csv names it as the Apt stack
// append helper this TU's interpreter calls, and the retail bytes are already
// in the link as the gen-dump row ?d_008cc690@@YAXXZ (687 B,
// game/gen_asm/d_008cb600.asm). The body is thiscall with six stack
// arguments (it reads context/scope/name/value and the three flags at
// [esp+0x10..0x40] and leaves a plain ret), which is exactly the call shape
// the two sites below emit: push value, name, scope, context and the three
// ints, this in ecx. Bind the ledger name to the retail body rather than
// inventing a second definition; alias_guard compares both pins at
// 0x008CC690 and sees one body. This links the interpreter; it is not
// conversion progress for the helper itself.
#pragma comment(linker, "/alternatename:?append@Rva8CD130State@@QAEXPAX0PAVRva8CD130String@@PAVRva8CD130Value@@HHH@Z=?d_008cc690@@YAXXZ")

class Rva8CD130State
{
public:
	void append(void *context, void *scope, Rva8CD130String *name,
		Rva8CD130Value *value, int a, int b, int c);
};

class BfmeA1232
{
public:
	void bfmePop1232(int count);
};

class Rva8CF1B0State
{
public:
	void addSegment(void *data, void *context, int size);
	void append(void *context, void *scope, BfmeStrVKI *name,
		Rva8CF1B0Value *value, int a, int b, int c);
	void popValues(int count);
	unsigned m_count;
	int m_unused04;
	Rva8CF1B0Value **m_stack;
	char m_gap0c[0x4c];
	Rva8CF1B0Value **m_slots;
	char m_gap5c[0x20];
	Rva8CF1B0Value *m_pending;
};

struct Rva8CF1B0Cursor { unsigned char *m_position; void *m_context; };
struct Rva8CF1B0Record
{
	unsigned m_firstSize;
	unsigned m_secondSize;
	unsigned m_thirdSize;
	unsigned char m_flags;
	unsigned char m_unused0d;
	unsigned char m_unused0e;
	unsigned char m_slot;
	const char *m_name;
};

class AptValue;
extern AptValue *g_bfmeFallbackDB;

void rva8CF1B0ProcessRecord(Rva8CF1B0State *state, Rva8CF1B0Cursor *cursor)
{
	int initialCount = state->m_count;
	unsigned char *aligned = (unsigned char *)(((unsigned)cursor->m_position + 3) & ~3u);
	Rva8CF1B0Record *record = (Rva8CF1B0Record *)aligned;
	cursor->m_position = aligned + 0x14;
	cursor->m_position += record->m_firstSize;
	cursor->m_position += record->m_secondSize;
	cursor->m_position += record->m_thirdSize;

	reinterpret_cast<Rva008CCED0BytecodeRunner *>(state)->run(
		aligned + 0x14, cursor->m_context, record->m_firstSize);
	Rva8CF1B0Value *pending = state->m_pending;
	if (pending != 0 && (record->m_flags & 1) != 0)
	{
		if ((record->m_flags & 4) != 0)
		{
			if (state->m_slots[record->m_slot] != 0)
				state->m_slots[record->m_slot]->release();
			state->m_slots[record->m_slot] = pending;
			pending->addRef();
		}
		else
		{
			BfmeStrVKI name(record->m_name);
			reinterpret_cast<Rva8CD130State *>(state)->append(cursor->m_context, 0,
				reinterpret_cast<Rva8CD130String *>(&name),
				reinterpret_cast<Rva8CD130Value *>(pending), 0, 1, 0);
		}

		state->m_pending->release();
		state->m_pending = 0;
		reinterpret_cast<Rva008CCED0BytecodeRunner *>(state)->run(
			aligned + 0x14 + record->m_firstSize,
			cursor->m_context, record->m_secondSize);
		if ((record->m_flags & 4) != 0)
		{
			state->m_slots[record->m_slot] = (Rva8CF1B0Value *)g_bfmeFallbackDB;
			pending->release();
		}
		else
		{
			BfmeStrVKI name(record->m_name);
			reinterpret_cast<Rva8CD130State *>(state)->append(cursor->m_context, 0,
				reinterpret_cast<Rva8CD130String *>(&name), 0, 0, 1, 0);
		}
	}

	if ((record->m_flags & 2) != 0)
	{
		pending = state->m_pending;
		if (pending != 0)
		{
			pending->addRef();
			state->m_pending->release();
			state->m_pending = 0;
		}
		unsigned *sizes = &record->m_firstSize;
		reinterpret_cast<Rva008CCED0BytecodeRunner *>(state)->run(
			(void *)(sizes[1] + sizes[0] + (unsigned)record + 0x14),
			cursor->m_context, sizes[2]);
		if (pending != 0 && state->m_pending == 0)
		{
			pending->addRef();
			state->m_pending = pending;
			pending->release();
		}
	}

	if (state->m_count > initialCount)
		reinterpret_cast<BfmeA1232 *>(state)->bfmePop1232(
			state->m_count - initialCount);
}


// MSVC 7.1 keeps separate retail false-return tails when their zero-code
// barrier tags differ. See shape_levers.md and the matched 00653990/003E5950
// witnesses. This candidate still requires native byte verification.
extern "C" void _WriteBarrier(void);
extern "C" void _ReadWriteBarrier(void);
#pragma intrinsic(_WriteBarrier)
#pragma intrinsic(_ReadWriteBarrier)

// Retail 0x008C6AD0, 233 bytes: registered value-conversion callback.
// The original callback name is unknown; keep the address in its name.
// The +4 flags and +8 Boolean payload follow AptValue_toNumber.cpp and
// AptBooleanCreate.cpp.  The validity bit follows Rva008C4A30Check.cpp.
class AptValue
{
public:
	float toNumber();
	bool isUndefined() const { return ((m_valueBits >> 15) & 1) == 0; }
	__forceinline bool isType(int type) const
	{
		return (m_valueBits & 63) == type && !isUndefined();
	}

	void *m_vtable;
	unsigned int m_valueBits;
	bool m_boolean;
};

class AptBoolean : public AptValue
{
public:
	static AptBoolean *Create(bool value);
};

// This is the already named twelve-byte stack prefix used by the adjacent
// 0x008C6800 callback.  In particular, the count is at VA 0x01338748;
// the old bank's g_bfmeCount1233 binding used a different image base.
struct Rva008AE770Stack
{
	int m_count;
	int m_rva0133874C;
	AptValue **m_rva01338750;
};
extern Rva008AE770Stack Rva008AE770TheStack;
extern const float g_rva01075350;

// The complete recovered predicate takes one stack pointer and returns AL.
// Its canonical declaration replaces the bank's void-function pointer cast.
bool __cdecl Rva008C4A30Check(Rva8CD130Value *value);

// Keep one shared numeric site in the structured main arm. The later
// coercion cases jump back to it; distinct tags retain both false suffixes.
AptValue *BooleanCoerce008C6AD0(void *, int count)
{
	if (count == 0)
		return g_bfmeFallbackDB;

	Rva008AE770Stack &stack = Rva008AE770TheStack;
	AptValue **args = stack.m_rva01338750;
	AptValue *value = args[stack.m_count - 1];
	int type = value->m_valueBits & 63;
	if (type >= 12 && type <= 19 && !value->isUndefined())
		goto common_true;
	if (type == 27 && !value->isUndefined())
		goto common_true;
	if (value == g_bfmeFallbackDB)
	{
		AptValue *result = AptBoolean::Create(false);
		_WriteBarrier();
		return result;
	}

	if (!value->isType(6) && !value->isType(7))
	{
		if (Rva008C4A30Check(reinterpret_cast<Rva8CD130Value *>(value)))
		{
			AptValue *result = AptBoolean::Create(false);
			_WriteBarrier();
			return result;
		}

numeric_value:
		if (value->toNumber() != g_rva01075350)
			goto common_true;

		{
			AptValue *result = AptBoolean::Create(false);
			_WriteBarrier();
			return result;
		}
	}

	if (type == 5)
	{
		bool result = value->m_boolean;
		return AptBoolean::Create(result);
	}
	if (type == 6)
		goto numeric_value;
	if (type == 7)
		goto numeric_value;
	{
		AptValue *result = AptBoolean::Create(false);
		_ReadWriteBarrier();
		return result;
	}

common_true:
	return AptBoolean::Create(true);
}
