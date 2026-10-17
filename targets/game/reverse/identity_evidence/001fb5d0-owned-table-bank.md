# Owned-table constructor bank, RVA 001FB5D0

The immutable alternative bank is
`targets/game/reverse/attempt_history/0x001fb5d0/ab179c2b23ba84faecadf377eed4a1b524cc6f61d8e61ad134cead5fa9c3f9c6.json`.
The preferred stash remains the earlier equal-scoring attempt.

This updated bank retains the native FireWeaponWhenDamagedBehavior class
declaration and uses the verified 348-byte dispatch block introduced by
ee47c5a9c2. Its first member initializer binds the five BFME tables before
initializing the eight weapon pointers. This preserves all 652 instruction
bytes and 42 relocation sites; body-level strict comparison also passes.

Requirements held with this attempt:

- In game/GameEngine/Include/GameLogic/Module/UpdateModule.h, initialize the
  existing m_pad field to -1 in the base constructor. The retail constructor
  stores -1 at both +18 and +1C. The graph reaches 626 ledger source files;
  these dependents have not been verified with the patch. A body-local field
  assignment does not reproduce the initialization order.
- Add the independently machine-proven compilation view:
  `??0Rva002D9B80UpgradeMux@@QAE@XZ,0x0003D24E,abi-view=??0Rva002D9B80@@QAE@XZ`.
  abi_view.view_verdict returns no refusal. The view has no arguments and a
  plain RET, and retail E8 calls reach the canonical 13-byte body through
  ILT 0003D24E. The bank renames only the header's UpgradeMux declaration
  through an address-qualified compilation view; it adds no callee identity.

The remaining strict failure is unrecorded_dir32_problem's precedence:
it checks for any differently recorded name at the base address before it
checks data_rows.csv. Thus all five references to the byte-verified
_g_Rva010A3DD4DispatchTables are refused because the record still contains
the MobMemberSlavedUpdate-labelled table name at 010A3DD4. This is reported
as false-reject dir32-recorded-name-precedence. No gate or record is edited.

The earlier attempt to promote the helper to a canonical UpgradeMux row
also encountered six legacy constructor identities. Its native 13-byte
implementation passed strict byte/DIR32 verification, but the original opaque
row and provider were restored after the identity gate refused promotion.
No helper landing is claimed. The ABI-view route avoids that identity claim
and is admitted by the dedicated image/ABI check.

The shared-header patch and unused ABI-view pin are reverted while this
constructor remains banked. The landed table data is independently complete
and byte-verified. Future promotion must resolve recorded-name ownership,
run the strict gate and verify all shared-header dependents.
