# Debug register-string data gate debts

Parent: 497cb4fc72. Four rows served by shard 1/4 have existing external
const char arrays in DebugExceptionhandler_LogRegisters.cpp. Retail Image.read
at each VA independently gives the text and terminating NUL below. Existing
LogRegisters consumers already use these same C-linkage address-derived names.
Define the arrays at their declarations, preserving all types and consumers.
No semantic rename, class/ABI change, pin, alias, donor evidence or body rewrite.

| Retail VA | Symbol | Retail text | Size including NUL |
| --- | --- | --- | --- |
| 0x01132DD4 | `_g_01132DD4` | `0x` | 3 B |
| 0x01134370 | `_g_01134370` | ` GS:` | 5 B |
| 0x01134388 | `_g_01134388` | ` SS:` | 5 B |
| 0x011343DC | `_g_011343DC` | ` EBX:` | 6 B |

add_data_match.py verifies each array's exact retail bytes, sizeof under normal
flags and zero relocations, and writes the data rows. All four exact keyed
pass-tests succeed first try and alone remove their baseline lines. The final
test verifies LogRegisters (1/1 function), 25 DIR32 references and all five
owned data rows in this unit. Normal scoped builds verify this unit and the FX
unit after the complete batch; normal commit hooks recheck both.

Batched with the same-pattern FX HeightOffset repair. Baseline entries shrink
917 to 912, with +32 B verified static data and +0 B exact C++. Linking gain is
unclaimed; local census dependencies are incomplete/stale.
