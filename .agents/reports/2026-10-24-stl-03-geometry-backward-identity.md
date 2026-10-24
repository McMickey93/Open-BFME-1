# GeometryShape copy-backward queue blocker

Queue item 235 claims `??$__copy_backward@PAUGeometryShape@@PAU1@H@_STL@@YAPAUGeometryShape@@PAU1@00ABUrandom_access_iterator_tag@0@PAH@Z`, retail RVA `0x000FCF70`, extent 123 bytes.

The retail body copies **forward**. `python3 tools/dis_retail.py 0x000fcf70 123` shows source ESI loaded from first, output EDI loaded from result, then `add esi, 0x24` at +0x66 and `add edi, 0x24` at +0x69. The existing supposedly canonical C++ explicitly increments both pointers too. STLport `_algobase.h` implements `__copy_backward` with `*--result = *--last`.

The census reports a wrong selected definition because ordinary template instantiation correctly emits a backward copy, whereas the pinned row names a forward-copy body. Removing those emitters would route backward operations to a forward routine. The safe repair requires independent caller identity and corrected ownership, not deleting the valid backward implementation. No source or pin change was retained.

BFME2 read-only comparison: `Code/GameEngine/Source/Common/System/GeometryShapeVectorCopyConstructor.cpp` confirms a 0x24-byte GeometryShape with StringBase at +0x1C and uses upstream STLport. No corresponding proven backward helper was found there. BFME1 retail remains the authority.

Validation: census-only `link_check.py GeometryShapeCopyBackward.cpp` reports selected non-retail definition, 0/123 linked bytes, census e9a5ae5b4c. Outcome blocked on identity; no linked-byte gain claimed.
