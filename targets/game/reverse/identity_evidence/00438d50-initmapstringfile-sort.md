# 0x00438D50 GameTextManager::initMapStringFile sorts with STLport sort, not qsort

Retail's initMapStringFile (matched in
GameTextManager_initMapStringFile_Thunk.cpp, 432 bytes) sorts the map lookup
table with STLport sort. Its introsort loop and final insertion sort are
out-of-line bodies reached through ILTs 0x000323F3 and 0x00007F4F. It never
calls the CRT qsort. Zero Hour's `qsort(..., compareLUT)` in GameText.cpp was a
present-unmatched copy that was not retail's body, and it is removed. The
thunk unit's `bfmeSortLookUp` names that STLport sort wrapper, so it does not
replace a descriptive name for the same call. The funclet row uw_00c22380 moved
with the parent, which is the only reason the two units are compared.
