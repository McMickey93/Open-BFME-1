# RVA 008AD8F0: text-binding layout update

The complete retail body is 603 bytes: ECX supplies the character receiver,
one pointer argument is popped by RET 4 at +0x258, and INT3 follows +0x25B.
The matched Rva008AF650SetMember caller invokes this body with the character
and its scope/context pointer. No original EA member spelling is claimed;
the recovered entry is Rva008AD8F0::method.

The two direct callees are the existing refresh@Rva008AD750StringBinding at
008AD750 and bfmeSetAxis1289@BfmeSlotState1289 at 008AC9F0. The host callback
slots and null sentinel use the already recorded global identities.

The old bank differs by an EBX/EBP mirror. A permutation's implicit-int local
incorrectly removed the final flags store; that candidate was rejected.
Returning a Boolean success result from the force-inlined layout helper and
setting m_flags6c at the caller join preserves every retail store and matches
all 603 bytes. The helper returns false for the existing clean guard and true
for both completed layout paths. This is a reconstruction shape, not an EA
helper-API identity claim.

Strict scoped build: 1/1 functions; three float constants and nine DIR32 sites
verified; body guard passes without exceptions. link_check before: new TU
unplaced. After: LINKED 0 -> 0 with 603 authored bytes; the existing sentinel,
empty-string and release-callback data names still lack link providers.

## Naming: no descriptive name is replaced (approved by the project lead 2026-10-16)

The banked attempt declared the host callback cell 0x01337870 as a TU-local
`g_aptTextLayout01337870`. That spelling was never a ledger identity: the cell is
owned by the matched data row `?g_bfmeSlot14VB@@3P6AXXZA` (data_rows.csv, VA
0x01337870, also recorded in dir32_addresses.csv), so the landed source reads that
owned name and casts it to the local `Rva008AD8F0LayoutCallback` typedef for the
call. The same holds for 0x01337874 (`?g_bfmeFreePair1286@@3P6AXPAXH@ZA`) and the
sentinel 0x012D5598 (`?g_bfmeSpecialBlock1286@@3DA`). name_regression pairs the
removed bank-only alias with the new typedef, which is a false pairing: the typedef
names a function-pointer type, not the cell, and no game/ source ever spelled
`g_aptTextLayout01337870`.
