# AddSubInternalFPF at 00879900

The already matched DoEmFloatIteration body at 0x0087A3B0 calls
AddSubInternalFPF twice, for operation bytes 0 and 1. Its parameter contract
and ordered SetInternalFPFNaN / choose_nan / StickyShiftRightMant /
ShiftMantRight1 / normalize helpers match BYTEmark's AddSubInternalFPF.
This is independent identity evidence for
`?AddSubInternalFPF@@YAXEPAUInternalFPF@@00@Z`; the old row was the opaque
`?d_00879900@@YAXXZ` dump. inputs/vendor/nbench/PROVENANCE.md identifies
retail as the pre-Dierks 2.1 release, whose emfloat code agrees here.

Retail starts at 0x00879900 after INT3. The executable portion ends in RET
at +0x345, followed by two alignment bytes, seven absolute switch targets
at +0x348, and 25 selector bytes at +0x364. The complete 893-byte extent
ends at +0x37D, followed by INT3. The scoped gate checks the emitted jump
table and selectors as well as code, rather than accepting only the earlier
154-byte guessed prefix.

Start from the banked 893-byte body, which differed only at +0x206 and
+0x20C: the inlined zero-mantissa OR reduction loaded two limbs in exchanged
positions. Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b,
Code/Libraries/Source/Benchmark/emfloat.c, supplies the useful source lever:
a constant index array inside the ordinary four-element OR loop delays
reassociation while preserving its loop-derived code shape. Its
IsMantissaZeroAddSub uses order {0,2,3,1}; the measured BFME 1 form uses
{0,2,1,3}, which emits retail's complete load sequence. Every limb is visited
once and OR remains commutative. A direct hand-unrolled reduction had changed
other instructions and did not reproduce retail.

Only AddSub calls the new inline IsMantissaZero00879900 helper. The original
35-byte IsMantissaZero and the independently landed Multiply helper are
unchanged. The bank's earlier control-flow correction is also retained:
the add/subtract arithmetic follows the unequal-exponent arm, rather than
being nested inside it. The two closing-brace moves and the scoped reduction
are the only changes to the existing emfloat.c. All compiler flags and shared
headers stay unchanged. The helper emits no standalone function, source
marker, global table, alias, pin, or assembly.

The approved existing emfloat.cpp compiles the .c as C++. The final AddSub
emission is 893 bytes with 24 relocation slots. All 19 home-TU ledger rows
pass strict byte, call, literal, constant, DIR32, and body checks. Existing
callee pins and imported memmove references resolve without a new binding.
link_check before the change reports LINKED 2198 -> 2923 bytes against the
census; the final source reports LINKED 2198 -> 3816 bytes. Current linked
coverage therefore grows by the full 893 bytes, with no previous loss.
Raw donor, probes and full gate/link receipts are build/sol3_fpf*,
build/add_00879900.txt and build/link_*00879900.txt in ds-9.
