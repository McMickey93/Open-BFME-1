# RNG data ownership prerequisite

The matched data rows added by BFME 1 commit 8756e25448 own the two
four-byte cells at VA 012D4CB8 and 012D4CBC in
game/GameEngine/Source/Common/D008790B0RandomSeed.cpp. Their initial values
are 13 and 117. The current provider build verifies both initializers against
retail and proves both symbol sizes. No data row, pin, function name, compiler
flag, function extent or C++ behavior changes here.

Four obsolete DIR32 registry names survived the ownership repair:
g_bfmeSeed790B0/g_bfmeSeedJC at 012D4CB8 and
g_bfmeCarry790B0/g_bfmeCarryJC at 012D4CBC. None occurs in game/ or
inputs/reference/shims/. tools/dir32_record.py retire accepts each deletion
for the already matched g_rva012D4CB8/g_rva012D4CBC owner. This removes
competing records rather than adding a binding or weakening a verifier.
The provider comment documents the two exact external symbols so the existing
repair_queue.py locator can find the unit by its keyed debt name.

Independent BFME 1 instructions establish the shared cells and ABI:

* RVA 008790B0, 72 bytes, loads carry at +15 and seed at +1B, writes carry
  at +39 and seed at +42, and returns with C3 at +47. Its reset path loads
  13 and 117. The existing address-derived identity is retained.
* RVA 00879100, 59 bytes, loads seed/carry at +0/+6, writes them at +2E/+25,
  computes the signed remainder by its one stack argument, and returns at +3A.
* RVA 00879140, 65 bytes, has the same loads/stores and an additional signed
  absolute-value tail; it returns at +40.

All three have no direct calls. These are 32-bit cdecl int interfaces with no
class layout. Disassembly and full scoped byte/relocation checks, rather than
equal source names, carry the relationship. Existing semantic names are not
expanded or newly inferred.

BFME 2 read-only master 16c3ea885a293dafc872dd5b67a59fa92b1d6407 was
searched for these cells and names. Its reverse/functions.csv identifies
Code/GameEngine/Source/Common/randnum.cpp as an earlier BFME 1 transfer;
the source uses its own g_bfmeSeedJC/g_bfmeCarryJC externs. That is not a
repair to import into BFME 1. BFME 1 commit 8756e25448 and the target's own
data/operand evidence establish this repair. The pinned donor checkout remains
unchanged.

Acceptance: both repair_queue.py pass-test commands pass after retirement and
remove the two keyed exemptions (1017 -> 1015). Before retirement the first
pass-test failed on the competing registry owner and restored its exemption.
The final provider build verifies 1/1 function, 2/2 data rows and all four
DIR32 references with no body exemptions. Both consumer units pass 3/3 rows
each, including their other matched bodies; their four and six DIR32
references pass without exemptions. CSV validation, find_declared_unmatched
for the documented provider and diff whitespace checks pass.

link_check.py on the provider with --compile-limit 0 before and after reports
LINKED PREVIEW UNKNOWN: 22,656 census objects are unavailable or stale.
The census's 72 -> 72 display is not measured new linked coverage. Authored
and retail exact C++ coverage remain +0. The verified improvement is two fewer
gate debts and retirement of four unused competing records, completing the
existing RNG data-ownership prerequisite.
