# Task 24: keep Q3's inline comparison local

Queue rank 29, claim 0xF4AFF57E. Moved Q3's existing inline no-case comparison into a TU-static helper. The partition still inlines all four retail `_memicmp` IAT calls; the object no longer exports its incompatible StringBase<char>::compareNoCase body under the globally owned identity. The static helper has COFF storage class 3, so it cannot compete with the canonical body.

`callees.py 0x009CCC50 503` independently lists four MSVCR71.dll!_memicmp calls at IAT VA 0x01359310 plus existing StringBase ownership helpers. `./build.sh` passes all 503 bytes, four empty-string references, and four DIR32 references. No global pin, shared header, or ledger change.

Before `link_check.py --census-only <file>`: compareNoCase COMDAT is not retail's body (the queue historically classified duplicate ownership). After the same check: source LINKS 503 bytes, with the compareNoCase blocker gone. These are changed-object diagnostics against the Oct 19 census, not a fresh global link.

BFME2 supporting source: `Code/Libraries/Source/WWVegas/WWLib/string_base.h` owns the external compareNoCase API. The Q3 inline shape is justified by BFME1's own IAT and byte evidence, without exporting that local shape as the canonical implementation.
