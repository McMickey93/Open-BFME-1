// stlport
// cl: /DNDEBUG /MD /O2 /EHsc /D_STLP_USE_STATIC_LIB

struct BfmeNodeZN
{
    BfmeNodeZN *m_bfmeNextZN;
};

class Rva0035E710Owner
{
public:
    void bfmeDoZN(void *a, BfmeNodeZN **link, void *what);
};

namespace Rva0035E510 {
class BfmeNodeEAT
{
public:
    void bfmeLinkEAT(BfmeNodeEAT *node, int *a, int *b);
};
}

// bfmeRelinkEAT is the body at 0x0035D9B0, linked as the gen-dump
// ?d_0035d9b0@@YAXXZ, so the thiscall is reached through a member-pointer
// call (the pattern the Apt callers of ?d_008cc940 use).
extern void d_0035d9b0();
typedef void (Rva0035E510::BfmeNodeEAT::*Rva0035D9B0Relink)(Rva0035E510::BfmeNodeEAT *node, int *a, int *b);

class BfmeOwnerXQ
{
public:
    int bfmeMoveXQ(BfmeOwnerXQ *source, int from);
};

struct Rva0035E5A0Link
{
    Rva0035E5A0Link *next;
    int index, extra;
};

struct Rva0035E5A0Record
{
    char pad00[0xC];
    char released, pad0D;
    short count;
    struct Rva0035E5A0Entry *first;
};

struct Rva0035E5A0Entry
{
    Rva0035E5A0Entry *next;
    int field04;
    int *child08, *child0C;
};

struct Rva0035E5A0OwnerView
{
    int field00;
    int *head04, *head08;
    char table0C[0xC];
    Rva0035E5A0Record *records;
};

// ?bfmeDoZN@Rva0035E710Owner@@QAEXPAXPAPAUBfmeNodeZN@@0@Z
void Rva0035E710Owner::bfmeDoZN(void *a, BfmeNodeZN **link, void *what)
{
    Rva0035E5A0OwnerView *source = (Rva0035E5A0OwnerView *)a;
    Rva0035E5A0OwnerView *self = (Rva0035E5A0OwnerView *)this;
    Rva0035E5A0Link **slot = (Rva0035E5A0Link **)link;
    int **firstSlot, **secondSlot;
    int *first, *second;
    {
        int extra = (*slot)->extra;
        int inputIndex = (*slot)->index;
        Rva0035E5A0Record *record = &source->records[inputIndex];
        int recordCount = record->count;
        Rva0035E5A0Entry *entry = record->first;
        if (recordCount > extra) {
            int count = recordCount - extra;
            do {
                --count;
                entry = entry->next;
            } while (count);
        }
        firstSlot = &entry->child08;
        secondSlot = &entry->child0C;
        first = entry->child08;
        entry->child08 = 0;
        second = entry->child0C;
        entry->child0C = 0;
    }
    int moveIndex = (*slot)->index;
    int index = ((BfmeOwnerXQ *)self->table0C)->bfmeMoveXQ((BfmeOwnerXQ *)source->table0C, moveIndex);
    if (index != -1) {
        (*slot)->index = index;
        (*slot)->extra = self->records[index].count;
        Rva0035E5A0Link *next = (*slot)->next;
        (*slot)->next = *(Rva0035E5A0Link **)what;
        *(Rva0035E5A0Link **)what = *slot;
        *slot = next;
        Rva0035E510::BfmeNodeEAT *receiver = (Rva0035E510::BfmeNodeEAT *)this;
        receiver->bfmeLinkEAT((Rva0035E510::BfmeNodeEAT *)source, (int *)&first, (int *)firstSlot);
        if (first) {
            int **tail = &source->head04;
            while (*tail)
                tail = (int **)*tail;
            *tail = first;
        }
        union { void (*fn)(); Rva0035D9B0Relink call; } relink = { d_0035d9b0 };
        (receiver->*relink.call)((Rva0035E510::BfmeNodeEAT *)source, (int *)&second, (int *)secondSlot);
        if (second) {
            int **tail = &source->head08;
            while (*tail)
                tail = (int **)*tail;
            *tail = second;
        }
    } else {
        *firstSlot = first;
        *secondSlot = second;
    }
}
