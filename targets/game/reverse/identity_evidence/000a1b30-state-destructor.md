# 0x000A1B30 is State::~State (`??1State@@UAE@XZ`)

The 123-byte body at 0x000A1B30 was matched under the address-derived name
`??1Rva000A1B30Holder@@QAE@XZ`. Retail reaches it through the ILT thunk
0x00016725 (`jmp 0x4a1b30`, `python3 tools/dis_retail.py 16725 5`).

Callers that name it:

- the matched scalar deleting destructor `??_GState@@UAEPAXI@Z` (0x000A1B00)
  calls it through ILT 0x00016725;
- 30+ matched derived state complete destructors (AIGuardIdleState,
  AIGuardInnerState, AIQuarrelState, AIRampageState, TurretState,
  DozerPrimaryIdleState, GiantBird*State, ActAsDozerState, FailureState, ...;
  `rg "ILT 0x00016725|ILT 0x16725" functions.csv`) are each a bare tail jump to
  that thunk, which their sources spell as the implicit base call to
  `??1State@@UAE@XZ`. symbols.csv already pins `??1State@@UAE@XZ` at 0x00016725
  and 0x000A1B30.

The body fits Zero Hour's `State : public MemoryPoolObject, public Snapshot`
destructor as BFME lays it out: destroy the 12-byte-element STLport vector at
+0x10 (node_alloc free), then the inline `~Snapshot` stores the Snapshot
vftable (VA 0x01073744 = `??_7Snapshot@@6B@`, RVA 0x00C73744) at +0. State's
own vptr store is dead and `__declspec(novtable)` keeps it out.

The source now defines `State::~State` (virtual) on `State : public Snapshot`;
the bytes are unchanged.
