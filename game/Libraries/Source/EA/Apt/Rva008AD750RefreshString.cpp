// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// RVA 008AD750: one scope argument; strings at +18/+1C; flags at +6C.
// Layout and call evidence: docs/analysis/0x008985c0.md and retail body.
#include <string.h>
struct BfmeStringData3AF0 { unsigned short m_refCount, m_length, m_capacity, m_unknown06; };
struct BfmeStringPool3AF0 { void *m_unknown00; void (__cdecl *free)(void *); };
class EAStringC { public: class StringDataC; };
extern EAStringC::StringDataC g_rva012D5298Empty;	// shared empty string block 0x012D5298
static inline BfmeStringData3AF0 *sharedEmptyString012D5298()
{
	return (BfmeStringData3AF0 *)&g_rva012D5298Empty;
}
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;
class BfmeStrVKI {
public:
    __forceinline BfmeStrVKI() {
        m_data = sharedEmptyString012D5298();
        ++m_data->m_refCount;
    }
    BfmeStrVKI(const char *text) { bfmeSetVKI(text); }
    void bfmeSetVKI(const char *text);
    __forceinline ~BfmeStrVKI() {
        BfmeStringData3AF0 *old = m_data;
        if (--old->m_refCount == 0) g_rva01337A30AllocPair->free(old);
    }
    __forceinline BfmeStrVKI &operator=(const BfmeStrVKI &source) {
        ++source.m_data->m_refCount;
        BfmeStringData3AF0 *old = m_data;
        if (--old->m_refCount == 0) g_rva01337A30AllocPair->free(old);
        m_data = source.m_data;
        return *this;
    }
    __forceinline unsigned length() const { return m_data->m_length; }
    __forceinline bool operator==(const BfmeStrVKI &other) const {
        unsigned left = length();
        unsigned right = other.length();
        return left == right && (m_data == other.m_data || memcmp(m_data + 1, other.m_data + 1, left) == 0);
    }
    BfmeStringData3AF0 *m_data;
};
class Rva8CD130String;
class Rva8CD130Value {
public:
    void getName(Rva8CD130String *output);
    __forceinline bool undefined() const { return (~(m_flags >> 15) & 1) != 0; }
    __forceinline Rva8CD130Value *parent() { return m_unknown4c; }
    void *m_unknown00;
    unsigned m_flags;
    char m_gap08[0x44];
    Rva8CD130Value *m_unknown4c;
    __forceinline bool kind13() const { return (m_flags & 0x3f) == 13 && !undefined(); }
    __forceinline bool kind18() const { return (m_flags & 0x3f) == 18 && !undefined(); }

};
class Rva00899770;
struct Rva008AE770Stack {
};
// Body at 0x008cc940: ?d_008cc940@@YAXXZ. The retail callee is linked as a
// cdecl void() body, so the thiscall string-creation method is reached
// through a member-pointer call (the pattern Rva8CEDA0PushConstantVariable.cpp
// and Rva8CD520ConfigureState.cpp use).
extern void d_008cc940();
typedef Rva00899770 *(Rva008AE770Stack::*Rva008AE770CreateString)(void *, int, BfmeStrVKI *, int, int, int);
extern Rva008AE770Stack Rva008AE770TheStack;
struct Rva008AD750TextSource { char m_gap00[0x34]; const char *m_text34; };
class Rva008AD750StringBinding {
public:
    void refresh(Rva8CD130Value *scope);
    char m_gap00[0x0c];
    Rva008AD750TextSource *m_unknown0c;
    char m_gap10[8];
    BfmeStrVKI m_string18;
    BfmeStrVKI m_string1c;
    char m_gap20[0x4c];
    unsigned m_flags6c;
};
void Rva008AD750StringBinding::refresh(Rva8CD130Value *scope)
{
    BfmeStrVKI &key = m_string1c;
    if (key.m_data == sharedEmptyString012D5298()) return;
    if (((char *)key.m_data)[8] == '$') return;
    BfmeStrVKI output;
    while (scope) {
        if (scope->kind13()) break;
        if (scope->kind18()) break;
        Rva8CD130Value *next = scope->m_unknown4c;
        if (!next) break;
        scope = scope->parent();
    }
    union { void (*fn)(); Rva008AE770CreateString call; } u = { d_008cc940 };
    Rva8CD130Value *value = (Rva8CD130Value *)(Rva008AE770TheStack.*u.call)(scope, 0, &key, 1, 1, 0);
    if (value->undefined()) output = BfmeStrVKI(m_unknown0c->m_text34);
    else value->getName((Rva8CD130String *)&output);
    if (!(m_string18 == output)) {
        m_string18 = output;
        m_flags6c = (m_flags6c & ~1U) | 2;
    }
}
