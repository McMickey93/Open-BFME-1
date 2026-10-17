// Retail 008B9850: arraySortScriptFunction literal; two tagged arguments.
// AptValue +04 flags and virtual slots 00/04 witnessed by this body.
class AptValue {
public:
    virtual void retain();
    virtual void release();
    unsigned m_valueBits;
    int toInteger() const;
    bool permanent() const { return ((m_valueBits >> 30) & 1) != 0; }
};
class Rva008CF740Value;
class Rva008CF740 { public: void run(Rva008CF740Value *, Rva008CF740Value *, int); };
class BfmeR1226 { public: void bfmeLine1226(char *); };
// 0x01338748: the Apt stack depth global, defined in Rva00C6DCC0StaticInit.cpp.
// Its address is also what this body passes as the interpreter receiver.
struct Rva008AE770Stack
{
	int m_count;
	int m_rva0133874C;
	AptValue** m_rva01338750;
};
extern Rva008AE770Stack Rva008AE770TheStack;
static Rva008CF740Value *Rva01338450SortFunction;
static Rva008CF740Value *Rva01338454SortReceiver;
static void push(AptValue *v) {
    Rva008AE770TheStack.m_rva01338750[Rva008AE770TheStack.m_count++] = v;
    if (!v->permanent()) v->retain();
}
int arraySortScriptFunction008B9850(unsigned *a, unsigned *b) {
    if (!Rva01338450SortFunction) return 0;
    AptValue *left = (AptValue *)(*a & ~1u);
    AptValue *right = (AptValue *)(*b & ~1u);
    push(right);
    push(left);
    ((Rva008CF740 *)&Rva008AE770TheStack)->run(Rva01338454SortReceiver, Rva01338450SortFunction, 2);
    ((BfmeR1226 *)&Rva008AE770TheStack)->bfmeLine1226("arraySortScriptFunction");
    int result = Rva008AE770TheStack.m_rva01338750[Rva008AE770TheStack.m_count - 1]->toInteger();
    AptValue *top = Rva008AE770TheStack.m_rva01338750[Rva008AE770TheStack.m_count - 1];
    if (!top->permanent()) top->release();
    --Rva008AE770TheStack.m_count;
    return result;
}

// Retail 008B9930: sort a tagged array value in place; with no arguments by
// value (comparator 008B90F0), else through the script function on top of the
// Apt stack, which this TU's comparator above reads from the two callbacks.
struct Rva008B9930Value {
    void *vptr;
    union { unsigned flags; struct { unsigned kindBits:6; unsigned remaining:26; }; };
    char field08[0x18];
    unsigned *field20;
    unsigned field24;
    unsigned field28;
    unsigned kind() const { return kindBits; }
    unsigned char invalid() const { return (unsigned char)~(flags >> 15) & 1; }
};
struct Rva008B9930Callback { char head[0x28]; Rva008CF740Value *receiver; };
extern AptValue *g_bfmeFallbackDB;
extern "C" int __cdecl compareValues008B90F0(unsigned *, unsigned *);
typedef int (__cdecl *Rva008B9930Compare)(unsigned *, unsigned *);
extern "C" void __cdecl qsort(void *, unsigned, unsigned, Rva008B9930Compare);
AptValue *rva008B9930(Rva008B9930Value *value, int argc) {
    if(value->kind()==22 && !value->invalid()) {
        if(argc==0) {
            qsort(value->field20, (unsigned)value->field28, 4, compareValues008B90F0);
            return g_bfmeFallbackDB;
        }
        int count=Rva008AE770TheStack.m_count;
        Rva008B9930Callback *top=(Rva008B9930Callback*)Rva008AE770TheStack.m_rva01338750[count-1];
        unsigned n=value->field28;
        Rva01338450SortFunction=(Rva008CF740Value*)top;
        Rva01338454SortReceiver=top->receiver;
        qsort(value->field20, n, 4, arraySortScriptFunction008B9850);
    }
    return g_bfmeFallbackDB;
}
