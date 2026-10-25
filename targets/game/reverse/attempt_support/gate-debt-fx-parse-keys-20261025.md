# FX parse-key data ownership gate debts

Parent: 9e67426596. All ten entries were served by the shard 1/4 repair queue.

BFME 1 target evidence: Image.read at each listed retail VA yields the text
below followed by NUL. Existing references in the FX bulk unit use precisely
these address-derived external const-char-array symbols as parse/INI keys.
Define each existing array in place, preserving namespace, type, symbol and
consumer expression. No class, layout, ABI, body or inferred name changes.
No donor source or address evidence is used.

| Retail VA | Text | Verified size including NUL |
| --- | --- | --- |
| 0x0109D84C | `Speed` | 6 B |
| 0x010F19FC | `Amplitude2` | 11 B |
| 0x011137D0 | `SinkOnTerrainCollision` | 23 B |
| 0x01113824 | `Shader2` | 8 B |
| 0x0111385C | `Shader1` | 8 B |
| 0x01113E20 | `StartPoint` | 11 B |
| 0x011142A4 | `Phase3` | 7 B |
| 0x011142BC | `Amplitude3` | 11 B |
| 0x011142E4 | `Phase1` | 7 B |
| 0x01114434 | `EventFX` | 8 B |

add_data_match.py verifies each emitted symbol against retail and checks its
C++ sizeof under the normal build flags. The tracked data rows cover only the
NUL-terminated arrays, excluding allocation padding; none has a relocation.
The tool adds the rows, and the exact keyed repair_queue.py pass-tests alone
remove the ten baseline exceptions. All ten pass on their first attempt.

The final keyed test verifies 470/470 functions, 24 string literals, 93 float
constants, 1042 DIR32 references and 19 data rows in the unit. A normal scoped
build and commit hooks verify the final batch. Debt entries shrink 927 to 917.
This adds 100 verified static data bytes and +0 B exact C++; credited progress
is the retirement of ten gate exceptions. No current linking gain is claimed.
