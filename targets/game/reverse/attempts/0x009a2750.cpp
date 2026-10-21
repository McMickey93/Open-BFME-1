// ?merge@CollisionManagerImpl@@QAEXXZ
// partial score=0.9304 date=2026-10-20
// CollisionManagerImpl::merge, retail 0x009A2750 (460 B; UpdateSort in
// collisionmanager_impl.cpp declares it as rva009A2750 -- rename on landing): the
// bottom-up merge sort of each axis endpoint list that UpdateSort (0x009A3AD0)
// calls on its rebuild path. Four 12-byte {head,tail,count} queues on the
// stack; the list is dealt alternately into queues 0/1, merged in runs of
// 1,2,4.. into 2/3 and back, then the prev links are rebuilt.
// State (2026-10-20): this spelling is 460/460 bytes with 32 differing, all at
// +0x88..+0xa6: retail computes b as `lea ebx,[esp+eax+0x38]` before the count
// resets, ours `lea ebx,[edi+0xc]` after the a->count test (b=&a[1]).
// Writing b=&lists[source+1] gives the right lea but flips the whole body's
// callee-saved assignment (zero/right ebp->ebx, head/b ebx->ebp/edi; 283 B).
// Tried without effect: decl order (C89 permutations), references, pointer
// head cursor, inline SortChain methods, __forceinline helper, loop shapes,
// all /Ob /G flags (flag_sweep), rotation_sweep.
// cl: /O2 /Ob1
typedef float Real;
class Rva009A45A0CollisionData;
struct Rva009A3AD0Endpoint
{
	Rva009A3AD0Endpoint *m_prev;	// +0x00
	Rva009A3AD0Endpoint *m_next;	// +0x04
	class Rva009A45A0CollisionData *m_node;	// +0x08
	unsigned int m_isMax : 1;	// +0x0c
	Real value;	// +0x10
};
class CollisionManagerImpl
{
public:
	void merge();
	Rva009A45A0CollisionData *m_root;	// +0x00
	unsigned int m_nodeCount;	// +0x04
	Rva009A45A0CollisionData *m_dirty;	// +0x08
	Rva009A3AD0Endpoint *m_axisHeads[3];	// +0x0c
	unsigned char m_table[0xAE10 - 0x18];
	unsigned char m_table2[0xC068 - 0xAE10];
	unsigned int m_axisCount;	// +0xc068
	bool m_rebuild;	// +0xc06c
};

struct SortChain {
    Rva009A3AD0Endpoint *head, *tail;
    unsigned count;
};
void CollisionManagerImpl::merge()
{
    for(unsigned index=0;index<m_axisCount;++index) {
        SortChain lists[4];
        unsigned side=0;
        lists[0].count=lists[1].count=0;
        lists[0].head=0;
        Rva009A3AD0Endpoint *node=m_axisHeads[index];
        while(node) {
            Rva009A3AD0Endpoint *next=node->m_next;
            node->m_next=lists[side].head;
            lists[side].head=node;
            ++lists[side].count;
            side ^= 1;
            node=next;
        }
        unsigned source=0;
        unsigned run=1;
        while(lists[source+1].count) {
            SortChain *a=&lists[source];
            unsigned output=source^2;
            SortChain *b=&a[1];
            lists[output].count=lists[output+1].count=0;
            while(a->count) {
                unsigned right=run, left=run;
                SortChain *d=&lists[output];
                for(;;) {
                    SortChain *chosen;
                    if(left && a->count) {
                        if(right && b->count && a->head->value>b->head->value) { chosen=b; --right; }
                        else { chosen=a; --left; }
                    } else if(right && b->count) {
                        chosen=b; --right;
                    } else break;
                    --chosen->count;
                    Rva009A3AD0Endpoint *picked=chosen->head;
                    chosen->head=picked->m_next;
                    if(d->count==0) d->head=picked; else d->tail->m_next=picked;
                    d->tail=picked;
                    ++d->count;
                }
                output^=1;
            }
            source^=2;
            run<<=1;
        }
        if(lists[source].count>1) lists[source].tail->m_next=0;
        m_axisHeads[index]=lists[source].head;
        m_axisHeads[index]->m_prev=0;
        for(Rva009A3AD0Endpoint *p=m_axisHeads[index];p->m_next;p=p->m_next)
            p->m_next->m_prev=p;
    }
}
