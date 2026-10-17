// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// RVA 008D1540: cdecl dispatch-table body, 350 bytes.
// docs/analysis/0x008985c0.md: both conversions use the same top value.
// The address-derived types describe only the accessed layout.
struct BfmeStringData3AF0 { unsigned short m_refs; };
struct BfmeStringPool3AF0 { void *m_unknown00; void (__cdecl *free)(void *); };
class EAStringC { public: class StringDataC; };
extern EAStringC::StringDataC g_rva012D5298Empty;	// shared empty string block 0x012D5298
static inline BfmeStringData3AF0 *sharedEmptyString012D5298()
{
	return (BfmeStringData3AF0 *)&g_rva012D5298Empty;
}
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;

class Rva8CD130String
{
public:
    __forceinline Rva8CD130String() {
        m_block = sharedEmptyString012D5298();
        ++m_block->m_refs;
    }
    __forceinline ~Rva8CD130String() {
        BfmeStringData3AF0 *old = m_block;
        if (--old->m_refs == 0) g_rva01337A30AllocPair->free(old);
    }
    BfmeStringData3AF0 *m_block;
};
class AptValue { public: int toInteger() const; };
class Rva8CD130Value
{
public:
    virtual void addRef();
    virtual void release();
    void getName(Rva8CD130String *);
    unsigned m_flags;
};
class Rva8D0D80Result : public Rva8CD130Value {};
class Rva8D0D80State
{
public:
    int m_count;
    int m_unknown04;
    Rva8CD130Value **m_stack;
};
struct Rva008D1540Context { void *m_unknown00; void *m_unknown04; void *m_scope08; };
extern AptValue *g_bfmeFallbackDB;
// The create call reaches retail 0x008D0080, whose ledger row is the matched
// gen dump ?d_008d0080@@YAXXZ (game/gen_asm/d_00882630.asm), as
// tools/callees.py 0x8d1540 350 prints.  Nothing defines the pinned
// ?create@Rva8D0D80State@@QAEPAVRva8D0D80Result@@PAX00HH@Z, so the call names
// the dump through a raw pointer bridge that keeps the thiscall shape.
void d_008d0080();

void rva008D1540ConvertPairDispatch(Rva8D0D80State *state, Rva008D1540Context *context)
{
    Rva8CD130Value *under = state->m_stack[state->m_count - 2];
    Rva8CD130Value *number = state->m_stack[state->m_count - 3];
    Rva8CD130Value *top = state->m_stack[state->m_count - 1];
    Rva8CD130String first;
    top->getName(&first);
    int count = ((AptValue *)number)->toInteger();
    Rva8CD130String second;
    top->getName(&second);
    union
    {
        void (*raw)(void);
        Rva8D0D80Result *(Rva8D0D80State::*typed)(void *, void *, void *, int, int);
    } create;
    create.raw = &d_008d0080;
    Rva8D0D80Result *result = (state->*create.typed)(under, context->m_scope08, &first, count, 1);
    for (int index = 1; index <= 3; ++index) {
        Rva8CD130Value *old = state->m_stack[state->m_count - index];
        if (!((unsigned char)(old->m_flags >> 30) & 1)) old->release();
    }
    state->m_count -= 3;
    if (result) {
        state->m_stack[state->m_count++] = result;
        if (!((unsigned char)(result->m_flags >> 30) & 1)) result->addRef();
        result->release();
    } else {
        Rva8CD130Value *fallback = (Rva8CD130Value *)g_bfmeFallbackDB;
        state->m_stack[state->m_count++] = fallback;
        if (!((unsigned char)(fallback->m_flags >> 30) & 1)) fallback->addRef();
    }
}
