// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// 008B9CC0: concatenate a type-22 array and stack values, flattening array operands.
// Base size 20h and array fields 20h/24h/28h are witnessed by constructor and reserve.
class BfmeItemDX;
void bfmePush(BfmeItemDX *);
extern void *(*Rva008C5D70Alloc)(unsigned);
extern "C" void *bfmeVft1030C[];
class Rva00899F00Base {
public:
    Rva00899F00Base(unsigned, int);
    virtual ~Rva00899F00Base();
    unsigned flags;
    char field08[0x18];
};
class Value008B9CC0 {
public:
    virtual void retain();
    virtual void release();
    virtual void slot08();
    virtual void slot0c();
    virtual void slot10();
    virtual unsigned char slot14();
    unsigned flags;
    unsigned char isType(unsigned char t) const { unsigned f=flags; return (f & 0x3f)==t && !((unsigned char)(~(f>>15)) & 1); }
};
class BfmeN1242 { public: void bfmeReserve1242(int); };
class AptValue;
class Rva008B9C90HeaderedDeleting : public Rva00899F00Base {
public:
    unsigned *m_elements;
    int m_capacity, m_length;
    virtual ~Rva008B9C90HeaderedDeleting();
    Rva008B9C90HeaderedDeleting() : Rva00899F00Base(0x16,8) {
        m_capacity=0; m_elements=0; m_length=0;
    }
    static void *operator new(unsigned n) {
        void *raw=Rva008C5D70Alloc(n+8); void *p=(char *)raw+8;
        bfmePush((BfmeItemDX *)p);
        return p;
    }
    __forceinline void put(int index, Value008B9CC0 *element) {
        Value008B9CC0 *old=(Value008B9CC0 *)(m_elements[index]&~1u);
        element->retain();
        if (old) old->release();
        unsigned tagged=(unsigned)element;
        if (element->slot14()==1) tagged|=1;
        m_elements[index]=tagged;
    }
    __forceinline void set(int index, Value008B9CC0 *element) {
        if (index>=0) {
            int next=index+1;
            ((BfmeN1242 *)this)->bfmeReserve1242(next);
            put(index,element);
            m_length = next > m_length ? next : m_length;
        }
    }
};
struct Rva008AE770Stack
{
	int field00;
	int m_rva0133874C;
	AptValue** m_rva01338750;
};
extern Rva008AE770Stack Rva008AE770TheStack;
extern AptValue *g_bfmeFallbackDB;
void *aptArrayConcat(Value008B9CC0 *self,int count) {
    if (self->isType(0x16)) {
        Rva008B9C90HeaderedDeleting *source=(Rva008B9C90HeaderedDeleting *)self;
        Rva008B9C90HeaderedDeleting *out=new Rva008B9C90HeaderedDeleting;
        for (int i=0;i<source->m_length;++i)
            out->set(out->m_length,(Value008B9CC0 *)(source->m_elements[i]&~1u));
        for (int j=0;j<count;++j) {
            Value008B9CC0 *v=reinterpret_cast<Value008B9CC0 *>(
                Rva008AE770TheStack.m_rva01338750[Rva008AE770TheStack.field00-j-1]);
            if (v->isType(0x16)) {
                Rva008B9C90HeaderedDeleting *array=(Rva008B9C90HeaderedDeleting *)v;
                for (int k=0;k<array->m_length;++k)
                    out->set(out->m_length,(Value008B9CC0 *)(array->m_elements[k]&~1u));
            } else out->set(out->m_length,v);
        }
        return out;
    }
    return g_bfmeFallbackDB;
}
