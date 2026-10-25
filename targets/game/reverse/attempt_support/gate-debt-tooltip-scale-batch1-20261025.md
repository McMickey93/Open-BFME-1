# DIR32 gate debt retirement batch: LanLobbyMenu and Scale2D

Input BFME 1 revision: `6f86c7f0ab`.
Touched units:
- `game/GameEngine/Source/Common/Rva009A9AD0Scale2D.cpp`
- `targets/game/reverse/body_guard_baseline.csv`
- `targets/game/reverse/dir32_addresses.csv`

## Retired DIR32 exceptions

Two DIR32 gate debts retired via machine `repair_queue.py pass-test`:

1. `dir32,0x008CE850,?playerTooltip@Rva004CE850LanLobbyMenu@@YAXPAVGameWindow@@PAVWinInstanceData@@I@Z`
   Retail VA `0x008CE850` was previously recorded as dump symbol `?d_004ce850@@YAXXZ`.
   The actual function is the matched, non-generated row `?playerTooltip@Rva004CE850LanLobbyMenu@@YAXPAVGameWindow@@PAVWinInstanceData@@I@Z` (in `LanLobbyMenuPlayerTooltip.cpp`).
   Retired `?d_004ce850@@YAXXZ` via `dir32_record.py retire '?d_004ce850@@YAXXZ' --for '?playerTooltip@Rva004CE850LanLobbyMenu@@YAXPAVGameWindow@@PAVWinInstanceData@@I@Z'`.
   Pass test passes and removes the baseline line.

2. `dir32,0x00DA9A20,?d_009a9a20@@YAXXZ`
   Retail VA `0x00DA9A20` is recorded in `dir32_addresses.csv` as `?Rva009A9A20@@YAXPBEHIIPAEHII@Z`, matching the matched row in `Rva009A9980Scale1D.cpp`.
   `Rva009A9AD0Scale2D.cpp` previously referenced the superseded dump declaration `d_009a9a20`. Updated to reference `Rva009A9A20`.
   Pass test passes and removes the baseline line.

## Verification

- `repair_queue.py pass-test` passed for both lines.
- `repair_queue.py verify-removed` exited 0.
- Scoped `./build.sh` on both files passed byte match and DIR32 address check.
- `body_guard_baseline.csv` shrank by 2 lines.
- `dir32_record_guard.py` verified the retirement trailer.
