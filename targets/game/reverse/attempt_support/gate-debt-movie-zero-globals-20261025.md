# Movie timing zero-data gate debts

Parent: aaa166fb9f. Three entries were served by shard 1/4 as unowned data.
Existing MovieFrame0040E9E0.cpp declarations and consumers establish the types
and address-derived symbols below; direct BFME 1 Image.read finds zero initial
bytes at both VAs. Define each existing variable with its existing type and
zero value, leaving all consumer expressions and function bodies unchanged.

| Retail VA | Existing symbol | Type | Extent |
| --- | --- | --- | --- |
| 0x012F126C | ?Trace0040E9E0@@3_NA | bool | 1 B |
| 0x012F1280 | ?Previous0040E9E0@@3_JA | __int64 | 8 B |

add_data_match.py verifies zero-filled storage and sizeof under build flags,
and alone writes both data rows. Both exact keyed pass-tests succeed first
try and alone retire their exemptions. The final keyed test verifies 1/1
function, 3 data rows, 2 literals, 1 float constant and 33 DIR32 references.
Normal scoped build and commit hooks verify the final source. Baseline
entries shrink 912 to 910; +9 B static data, +0 B exact C++. No donor inputs,
new names, ABI decisions, pins, aliases or linking gain are claimed.

## Skipped Threshold0040E9E0 (VA 0x012F1290)

The served entry said no datum owned this VA. Attempting an eight-byte zero
initial definition was refused by add_data_match before any keyed pass-test:
"0x012F1290 already owned by line 1538; one owner per address".
The existing row is ?g_Va012F1290@@3_JC, defined as volatile __int64 in
Display.cpp; the movie consumer currently declares a nonvolatile __int64 under
another name. The original source and data ledger were restored, and the
claim released. No second definition, new address-name global or type/view
reconciliation was attempted. This is a prerequisite for a future repair of
the stale unowned entry, not a failed body reconstruction. The existing data
row's evidence proves the full eight-byte cell via paired retail stores.
