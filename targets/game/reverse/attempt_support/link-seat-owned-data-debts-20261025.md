# Existing matched data ownership: three obsolete exemptions

At BFME 1 revision 3b375d6e2844, the gate-debt fallback served 1015 DIR32
exemptions. Three now have matched data owners and pass the normal keyed
`repair_queue.py pass-test` after deleting their individual exemptions. The
result is 1012 exemptions. This completes the verification prerequisite for
these existing data-ownership repairs; no function or data row, name, pin,
layout, compiler option, executable byte or verifier implementation changes.
The three source comments spell the exact existing COFF owners so the normal
repair-queue locator finds their defining units.

| Existing owner | Target evidence | Verification |
| --- | --- | --- |
| `?g_0108132C@@3QBUFieldParse@@B` | VA 0108132C, matched 32-byte FieldParse table, Texture/parseAsciiStringVectorAppend/+8 and zero terminator. Getter RVA 000C2A00 is `mov eax,0108132C; ret` (6 bytes). | Keyed pass-test: function 1/1, data 1/1, DIR32 1, zero body exemptions. WaterTextureList consumer: 1/1 functions and full references. |
| `?g_01336E79@@3_NA` | Existing matched one-byte zero-initialized flag. Debug finalizer writes it at RVA 0088B716 and 0088B779. | Keyed pass-test: defining unit data 2/2. Consumer DebugFinishAssert0088B530: 1/1 function, DIR32 20, 11 literals, 2 empty strings, bounded switch table, zero body exemptions. |
| `?g_013405E0@@3KA` | Existing matched four-byte zero cell. Retail RVA 00903170+29 stores EDX to VA 013405E0; EDX was loaded from OwnerThreadId. RET at +2F establishes full 48-byte extent. | Keyed pass-test: function 1/1, data 1/1, DIR32 6, zero body exemptions. |

The matched table/flag/dword identities and sizes are established by BFME 1's
existing data rows, target instructions, initial bytes and normal relocation
verification. The meanings of opaque names are not expanded. In particular,
this does not change the existing Debug body identity or its 948-byte extent.
Provider and consumer checks are separate from a link-clean claim.

Read-only BFME 2 master e2fdc5620c5834c1c98de24aa3510d72e2cbcc69 was
searched for these owner names and corresponding Common/debug/DX8 providers;
no donor repair was imported. Pinned BFME 2 beed8a16790a was left unchanged.
No donor address, layout or linking result establishes a BFME 1 fact here.

## Blocked work and resumption conditions

* Live W3DBridgeLoad link preview against census 32774ab033 takes 325 seconds
  and returns UNKNOWN, 0 -> 0 bytes: 524 changed/new ledger objects cannot be
  read here, so any name may be defined there. The previous non-retail
  findBridge emitter was already removed by eaa7e1c8fc. The artifact's 2832B
  queue estimate is not current linked coverage. Restore current dependency
  evidence or refresh the maintainer census before retrying this acceptance.
* VA 01080FC0 pooled string debt: function 1/1 and data 1/1 verify, but the
  keyed test fails six competing DIR32 records. `dir32_record.py retire`
  refuses g_aptPalantirBrightJewel because the active assembly dump
  game/masm_dumps/Rva0035F600ShowEndGame.asm still references it. No alternate
  deletion or pin was attempted. Prior 4389a342d4 converged eleven C++ users;
  the active dump remains a prerequisite.
* Apt VA 01337820 and VA 01338524/013385D8/01338678 already have matched
  owners and no competing registry names. Keyed tests still reject the
  Rva008B38F0Global/Rva008A9A70Str type fragments as the globals' addresses.
  Data 1/1 plus functions 2/2, and data 3/3 plus function 1/1, respectively,
  pass before the address check. Record this as false-reject dir32-name-address;
  resume after the maintainer fixes that checker. Do not rename or bypass it.
  All trial comments for rejected candidates were reverted and claims released.

Authored C++ and exact C++ coverage: +0 B. No newly linked byte claim.
The measured improvement is three fewer gate debts, with all three machine
pass-tests and provider/consumer checks passing. CSV validation, declared-
unmatched checks and whitespace checks also pass. No full build or census
build was started.
