# _STL::_Node_Alloc_Lock<true,0>::~_Node_Alloc_Lock

Retail 0x0082BDE0 (32 bytes, INT3-bounded) is an /Og- thiscall body that
tests the constant 1 and then calls the thiscall at 0x0082AD50 on the
object at VA 0x0130B254. Both addresses are already pinned independently:
0x0130B254 is `?_S_lock@?$_Node_Alloc_Lock@$00$0A@@_STL@@2VNodeAllocMutex@2@A`
(the lock the matched `__node_alloc<true,0>::_M_allocate` at 0x0082E540
acquires) and 0x0082AD50 is `?_M_release_lock@NodeAllocMutex@_STL@@QAEXXZ`.
`if (__threads) _S_lock._M_release_lock();` with `__threads == true` is the
STLport 4.5.3 `_Node_Alloc_Lock` destructor (inputs/vendor/stlport/stl/_alloc.h).

The matched `_M_allocate` 0x0082E540 (FuncInfo 0x00E43D90) has one unwind
action, the retail funclet 0x00C54970, which is `lea ecx,[ebp-0x15]` then
`jmp 0x0082BDE0`: it destroys that function's `_Node_Alloc_Lock<true,0>`
guard through this body. The out-of-line COMDAT that the guard's inline
destructor emits in STL_new_alloc_allocateThunk.cpp is byte-identical to
retail at all 32 bytes (relocations to `_S_lock` and `_M_release_lock`).

The previous claim `?grokIf1@BfmeIf1VMK@@QAEXXZ` was an opaque shape
reconstruction ("/Od if(1) member call on global 0x0130B254") with no
caller evidence; it is retired. The sibling 0x0082BDC0 (constant-0 test on
0x0130B250) is left as is.
