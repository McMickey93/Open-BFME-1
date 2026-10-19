// Address-derived identity: a two-key decrement/removal operation. The owning
// class is unknown; the verified layout is represented by explicit offsets.
// rva009A3960 is the matching two-key add (Open-BFME-2 0x00759490, a
// byte-identical body there; WorldBuilder places both in collisionmanager_impl).
#include <string.h>
#pragma intrinsic(memcpy)

void *__cdecl operator new(unsigned int bytes);

struct Rva009A3540PairNode
{
    struct Link
    {
        Link **backlink;
        Link *next;

    };

    unsigned char pad00[8];
    unsigned int key0;
    unsigned int key1;
    unsigned int counter;
    Link link14;
    unsigned int pad1c;
    Link link20;
    unsigned char pad28[8];
    Rva009A3540PairNode *next;
};
struct Rva009A3300Node;
class Rva009A3300HashTable
{
public:
    void remove(Rva009A3300Node *entry);
};
struct BfmeHolderZT;
struct BfmeNodeZT
{
    unsigned char head[0x2c];
    BfmeHolderZT *before;
    BfmeNodeZT *after;
};
struct Rva009A3770Node;
class Rva009A3770HashTable
{
public:
    Rva009A3770Node *insert(Rva009A3770Node *src);
};
class BfmeListZT
{
public:
    void bfmeFreeZT(BfmeNodeZT *node);
};
struct Rva009A3540OpaqueOwner
{
    unsigned char pad00[0x18];
    Rva009A3540PairNode *buckets[0x2b7b];
};

class Rva009A3540PairOwner
{
public:
    // Retail 0x009A3960, defined at the end of this file.
    void rva009A3960(Rva009A3540OpaqueOwner *first, Rva009A3540OpaqueOwner *second);

    void removePair(Rva009A3540OpaqueOwner *a, Rva009A3540OpaqueOwner *b);
};

void Rva009A3540PairOwner::removePair(Rva009A3540OpaqueOwner *a,
                                      Rva009A3540OpaqueOwner *b)
{
    unsigned int aGroup = *(unsigned int *)((char *)a + 0xa0);
    if (aGroup != 0 &&
        aGroup == *(unsigned int *)((char *)b + 0xa0))
        return;

    if (*(unsigned int *)((char *)a + 0x9c) >
        *(unsigned int *)((char *)b + 0x9c))
    {
        Rva009A3540OpaqueOwner *swap = a;
        a = b;
        b = swap;
    }
    unsigned int aId = *(unsigned int *)((char *)a + 0x9c);
    unsigned int bId = *(unsigned int *)((char *)b + 0x9c);

    unsigned int hash = (aId << 16) + bId;
    unsigned int bucket = hash % 0x2b7b;
    Rva009A3540PairNode *node = ((Rva009A3540PairNode **)((char *)this + 0x18))[bucket];
    while (node != 0 && (node->key0 != aId || node->key1 != bId))
        node = *(Rva009A3540PairNode **)((char *)node + 0x30);
    if (node == 0)
        return;

    if (node->counter == *(unsigned int *)((char *)this + 0xc068))
    {
        unsigned char keyRecord[44];
        *(unsigned int *)(keyRecord + 8) = aId;
        *(unsigned int *)(keyRecord + 0xc) = bId;
        ((Rva009A3300HashTable *)((char *)this + 0xae10))->remove(
            (Rva009A3300Node *)keyRecord);
    }

    --node->counter;
    if (node->counter != 0)
        return;

    if (node->link14.next)
        node->link14.next->backlink = node->link14.backlink;
    *node->link14.backlink = node->link14.next;
    // Capture the second link before clearing the first, as in retail.
    Rva009A3540PairNode::Link *next = node->link20.next;
    node->link14.backlink = 0;
    if (next)
        next->backlink = node->link20.backlink;
    *node->link20.backlink = node->link20.next;
    node->link20.backlink = 0;
    ((BfmeListZT *)((char *)this + 0x18))->bfmeFreeZT((BfmeNodeZT *)node);
}

// Retail 0x009A3960 (363 bytes): find the pair node for (a, b) or take one
// from the free list at +0xae04 (operator new(0x34) when empty), link it into
// its bucket and onto both owners' lists at +0x20; an existing node's counter
// is bumped and, on reaching the limit at +0xc068, the pair is queued in the
// table at +0xae10. The no-op conditionals are the shape that reproduces
// retail's register choice (as in Open-BFME-2's matched copy).
void Rva009A3540PairOwner::rva009A3960(Rva009A3540OpaqueOwner *a,
                                       Rva009A3540OpaqueOwner *b)
{
    unsigned int aGroup = (1 ? (*(unsigned int *)((char *)a + 0xa0))
                             : (*(unsigned int *)((char *)a + 0xa0)));
    if (aGroup != 0 &&
        aGroup == *(unsigned int *)((char *)b + 0xa0))
        return;

    if (*(unsigned int *)((char *)a + 0x9c) >
        *(unsigned int *)((char *)b + 0x9c))
    {
        Rva009A3540OpaqueOwner *swap = a;
        a = b;
        b = swap;
    }

    unsigned int aId = *(unsigned int *)((char *)a + 0x9c);
    unsigned int bId = *(unsigned int *)((char *)b + 0x9c);
    unsigned int bucket = ((aId << 16) + bId) % 0x2b7b;

    unsigned char buf[44];
    *(unsigned int *)(buf + 8) = aId;
    *(unsigned int *)(buf + 0xc) = bId;
    Rva009A3540PairNode *node =
        ((Rva009A3540PairNode **)((char *)this + 0x18))[(bucket ? bucket : bucket)];
    while (node != 0 && (node->key0 != aId || node->key1 != bId))
        node = *(Rva009A3540PairNode **)((char *)node + 0x30);
    if (node == 0)
    {
        *(unsigned int *)(buf + 0x10) = 1;
        *(Rva009A3540OpaqueOwner **)buf = a;
        *(Rva009A3540OpaqueOwner **)(buf + 4) = b;

        Rva009A3540PairNode *fresh = *(Rva009A3540PairNode **)((char *)this + 0xae04);
        if (fresh != 0)
            *(Rva009A3540PairNode **)((char *)this + 0xae04) =
                *(Rva009A3540PairNode **)((char *)fresh + 0x30);
        else
            fresh = (Rva009A3540PairNode *)operator new(0x34);

        memcpy(fresh, buf, 0x2c);

        Rva009A3540PairNode **slot =
            &((Rva009A3540PairNode **)((char *)this + 0x18))[(bucket ? bucket : bucket)];
        *(Rva009A3540PairNode ***)((char *)fresh + 0x2c) = slot;

        Rva009A3540PairNode *old = *slot;
        fresh->next = old;
        if (old != 0)
            *(Rva009A3540PairNode ***)((char *)old + 0x2c) = &fresh->next;
        *slot = fresh;

        Rva009A3540PairNode::Link **headA =
            (Rva009A3540PairNode::Link **)((char *)a + 0x20);
        fresh->link14.backlink = headA;
        Rva009A3540PairNode::Link *oldA = *headA;
        fresh->link14.next = oldA;
        if (oldA != 0)
            oldA->backlink = &fresh->link14.next;
        *headA = &fresh->link14;

        Rva009A3540PairNode::Link **headB =
            (Rva009A3540PairNode::Link **)((char *)b + 0x20);
        fresh->link20.backlink = headB;
        Rva009A3540PairNode::Link *oldB = *headB;
        fresh->link20.next = oldB;
        if (oldB != 0)
            oldB->backlink = &fresh->link20.next;
        *headB = &fresh->link20;

        *(Rva009A3540PairNode **)((char *)fresh + 0x28) = fresh;
        fresh->pad1c = (unsigned int)fresh;
        return;
    }

    unsigned int count = ++node->counter;
    if (count != *(unsigned int *)((char *)this + 0xc068))
        return;

    *(unsigned int *)(buf + 0x10) = 0;
    *(unsigned int *)(buf + 0xc) = bId;
    *(Rva009A3540OpaqueOwner **)buf = a;
    *(Rva009A3540OpaqueOwner **)(buf + 4) = b;
    *(unsigned int *)(buf + 8) = aId;
    ((Rva009A3770HashTable *)((char *)this + 0xae10))->insert((Rva009A3770Node *)buf);
}
