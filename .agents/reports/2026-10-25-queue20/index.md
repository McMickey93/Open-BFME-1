# Twenty queue tasks — 2026-10-25

The requested 80-minute wait completed before repository work began. This batch uses no sub-agents. Each task has a separate commit authored by Yannick Molinghen: 18 source repairs and two evidence-only blocker records (tasks 19–20).

All retained source edits pass BFME1 scoped byte and relocation checks, and normal commit hooks. These are linking repairs: most use declaration-only STL specializations to remove competing definitions and retain verified BFME1 providers. Task 17 restores the already-proven nontrivial record layout; task 18 aligns CRT/STL compiler settings with verified BFME1 siblings. Both make their emitted helpers retail-exact. They do not add new function conversions. Current global linking remains unknown because the census and current inputs differ; no aggregate linked-byte gain is claimed.

BFME2 supplied an applicable repair technique: sibling `../Open-BFME-2` revision `f301d686c70c3e5fa0b51b342a2745f495b8a0b1`, especially `Code/Libraries/Source/WWVegas/WWLib/RvaHashResize00927DE0.cpp` and commit `e9d93338e0`. BFME1 callers, providers, layouts, ABI and retail verification remain authoritative. No donor addresses were imported.

## Task table and evidence

| # | Queue rank | Change | Result | Evidence |
|---|---:|---|---|---|
| 1 | 9 | Hash resize for insertion at 0x000D6C60: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 1](task-01.md) |
| 2 | 10 | Hash resize for insertion at 0x000F6C10: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 2](task-02.md) |
| 3 | 11 | Hash resize for insertion at 0x00461360: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 3](task-03.md) |
| 4 | 12 | Hash resize for insertion at 0x004613F0: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 4](task-04.md) |
| 5 | 13 | Hash resize for insertion at 0x00469D20: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 5](task-05.md) |
| 6 | 14 | Hash resize for insertion at 0x00469FC0: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 6](task-06.md) |
| 7 | 15 | Hash resize for insertion at 0x0046AC80: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 7](task-07.md) |
| 8 | 16 | Hash resize for insertion at 0x0046AF20: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 8](task-08.md) |
| 9 | 17 | Hash resize for insertion at 0x0046C2A0: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 9](task-09.md) |
| 10 | 18 | Hash resize for insertion at 0x0046C540: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 10](task-10.md) |
| 11 | 19 | Hash resize for insertion at 0x00583B30: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 11](task-11.md) |
| 12 | 20 | Hash resize for insertion at 0x00614D10: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 12](task-12.md) |
| 13 | 21 | Hash resize for insertion at 0x00693020: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 13](task-13.md) |
| 14 | 22 | Hash resize for insertion at 0x0046C000: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 14](task-14.md) |
| 15 | 23 | Hash resize for insertion at 0x00614BC0: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 15](task-15.md) |
| 16 | 7 | Subtitle map resize: use verified provider(s), remove competing emitter(s) | Source repair verified; global link status unknown | [Task 16](task-16.md) |
| 17 | 31 | Module nugget copy: restore the proven nontrivial layout and retail copy helper | Source repair verified; global link status unknown | [Task 17](task-17.md) |
| 18 | 32 | Pointer vector overflow: align CRT/STL settings; preserve exact caller and helper | Source repair verified; global link status unknown | [Task 18](task-18.md) |
| 19 | 26 | Audio handle vector overflow: document blocker; all trials reverted | Blocked; evidence commit only | [Task 19](task-19.md) |
| 20 | 40 | State transition vector overflow: document blocker; all trials reverted | Blocked; evidence commit only | [Task 20](task-20.md) |

## Verification limits

Each of the first 15 resize repairs preserves all 23 rows in the insertion TU and verifies its dedicated provider. Task 16 preserves all three rows in the subtitle unit and verifies its resize provider. The other repairs verify every matched row in each edited TU and provider. COFF inspection independently confirms external references in the declaration-only repairs. Tasks 17 and 18 independently byte-verify their corrected 105-byte copy and 265-byte overflow helpers, including relocations. Normal hooks recheck each commit's changed sources. Final publication and claim-release status are reported in the conversation.

Initial stale queue entries already fixed by earlier work were skipped and do not count among these twenty tasks. Existing unrelated `.agents/` files were preserved. The BFME2 submodule initialization was kept separate from the source commits.
