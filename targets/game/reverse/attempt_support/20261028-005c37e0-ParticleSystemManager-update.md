# 0x005C37E0 ParticleSystemManager::update (467 B), bank 0.98

Bank: `targets/game/reverse/attempts/0x005c37e0.cpp` (session 466, a1), 467/467 B,
12 relocations, 9 non-reloc bytes. VC7.1 /O2 `/DNDEBUG /MD /EHsc`. Supersedes
the 0.26 bank.

Structure (all byte-verified except the residue): `m_bfmeUpdateTime(+0x94) = 0`;
QueryPerformanceFrequency/Counter when TheWritableGlobalData+0xA91; a local
BfmeParticleSystemHandle (EH state 0); skip flag = TheGameClient+0xC4 &&
!TheGameLogic+0x11D; Zero Hour's loop, with `sys = it->m_value` (inline
weak-handle assignment that unlinks from the old system's +0x98/+0x9C handle
list and appends to the new one), `if (!sys.m_system) continue;` (ZH's
no-advance bug), update gate `sys->+0x94 || skip`, `update(m_localPlayerIndex)`
at vtable +0x10, `++it; delete sys.m_system` on false; then the elapsed time
`(Real)diff * 1000.0f / (Real)freq` stored at +0x94; handle dtor through ILT
0x00013994 (pinned ??1BfmeParticleSystemHandle@@QAE@XZ).

Levers that mattered: `__forceinline` on the handle's operator= (else a
call, 330 B); `~BfmeParticleSystemHandle() throw();` removes the state -1
store before the final destructor call (475 -> 467 B).

Residue (+0x44, +0x17E..+0x1A1): retail's first QueryPerformanceCounter
target lives at [esp+1Ch] and receives the difference; the second lives at
[esp+14h]. Ours swaps the two slots. Inert: declaration order, block-scoped
end, `__int64` counters cast to LARGE_INTEGER*. `end.QuadPart -= start.QuadPart`
puts the QPC slots where retail has them but stores the difference into the
wrong one (11 B). A separate `elapsed`, a `(Real)(end - start)` temporary or a
three-member timer struct grow or reorder the frame (33-42 B). Observation
(VC7.1 slot order looks weight-driven): retail's slots fit start, end and
frequency all weighing the same, ordered by reverse first use.

Later inert trials (same session): dead extra references to `end`
(self-assign, a copy, a zero-valued `end - end` term), and mixed counter types
(`__int64` start or end with a LARGE_INTEGER partner) all keep the swapped
slots (9 B); `end = start` after the difference costs 8 B.

Session 467 (a1): slots read off the probe: frequency [esp+24h] in both;
retail start [1Ch] / end [14h], ours start [14h] / end [1Ch]. Further inert
(still 9 B): the difference through a `__forceinline` `bfmeTicks(end, start)`
helper, through `LARGE_INTEGER *ps = &start`, through
`const LARGE_INTEGER *pe = &end`, and as `-(start - end)`.
