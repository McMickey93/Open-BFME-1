# _STL::_Node_Alloc_Lock<false,0>::~_Node_Alloc_Lock

Retail 0x0082BDC0 (27 bytes, INT3-bounded) is an /Og- thiscall body that
tests the constant 0 (`xor eax,eax; je`) and would call the pinned
`?_M_release_lock@NodeAllocMutex@_STL@@QAEXXZ` (0x0082AD50) on VA
0x0130B250. That VA is the lock the matched node allocator at 0x0082E450
(`bfmeSmallAllocPR`, the `__node_alloc<false,0>` allocate path: it indexes
`__node_alloc<false,0>::_S_free_list` and calls the pinned
`__node_alloc<false,0>::_S_refill` 0x0082C870) acquires and releases in its
inlined guard, so it is `_Node_Alloc_Lock<false,0>::_S_lock`.
`if (__threads) _S_lock._M_release_lock();` with `__threads == false` is the
STLport 4.5.3 guard destructor (inputs/vendor/stlport/stl/_alloc.c).

The same parent's only unwind action, retail funclet 0x00C54950
(FuncInfo 0x00E43D6C), is `lea ecx,[ebp-0x15]; jmp 0x0082BDC0`: it destroys
that guard through this body. It is the `false` twin of 0x0082BDE0
(identity_evidence/0082bde0-stlport-node-alloc-lock-dtor.md). With the
guard declared as `_Node_Alloc_Lock<false,0>` (dtor specialized to keep the
unreferenced local retail's frame shows), the parent still matches and the
emitted COMDAT is byte-identical to retail at all 27 bytes.

The previous claim `?grokIf0@BfmeIf0VMJ@@QAEXXZ` was an opaque shape
reconstruction with no caller evidence; it is retired.
