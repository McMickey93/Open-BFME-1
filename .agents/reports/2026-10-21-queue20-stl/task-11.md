# Queue 11: AudioRequest list-node deallocation

Blocked by allocator configuration, with no source change. The first census
copy in GameAudio is 32 bytes and imports `__new_alloc::deallocate`. The Miles
copy is 47 bytes: it selects operator delete above 128 bytes and the node pool
below that threshold. Its COFF relocations identify both callees. The symbol
has no retail address in the census or current ledger; first-copy selection is
not proof that the Miles copy is wrong.

`callees.py 0x006A8DC0 864` independently decodes four calls to the node pool
at 0x0082E5F0. Changing the TU allocator configuration would risk replacing
that proven behavior. A blanket emitter suppression would bind its calls to
the conflicting first copy. No shared header, generated file, pin or baseline
was changed.

`./build.sh` on MilesAudioManagerRva006A8DC0.cpp passes 1/1 functions, five
DIR32 references and all scoped guards. `link_check.py --census-only` reports
0/1 linking, solely this allocator COMDAT first-copy difference. Before/after
are identical because the source is unchanged. The re_log entry uses the
synthetic queue claim key, not an invented body boundary.
