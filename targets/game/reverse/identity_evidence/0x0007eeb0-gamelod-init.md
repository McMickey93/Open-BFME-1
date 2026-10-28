# 0x0007EEB0 GameLODManager::init (1074 B)

BFME 1 target evidence:
- `ilt_oracle.py check ?init@GameLODManager@@QAEXXZ 0x0007EEB0`: CONFIRMED exact.
- Boundary: RET at +0x431, INT3 after; SEH frame, `sub esp,0x87c`.
- Literals Data\INI\GameLOD.ini, Data\INI\GameLODPresets.ini, FixedStaticGameLOD,
  Benchmark.txt / "BenchProfile = %s %d %f %f %f"; constants 0.94 and 1/256 MB.
- Callee ILT names (ilt_oracle, exact): refreshCustomStaticLODLevel 0x00023DAD
  (body 0x0007C1D0, ledger placeholder bfmeGo1144, pin rva0007C1D0),
  getIdealStaticGameDetail 0x0000D53A (body 0x00090900, ledger placeholder
  rva00090900IdealStaticGameDetail), getStaticGameDetail, getFixedStaticGameDetail,
  OptionPreferences ctor/dtor, UserPreferences::write, setStaticLODLevel, global
  testMinimumRequirements 0x0001391C -> 0x00718DA0 (jmp via ILT 0x00041E7A to
  W3DShaderManager::testMinimumRequirements 0x00717880).
- Field offsets read from the body: +0x16C4 fixed static detail (seeded from the
  ideal level and saved as FixedStaticGameLOD), +0x16CC current audio LOD
  (compared and stored, then TheAudio slot 92), +0x1738 CPU MHz threshold for the
  audio LOD. +0x16C0/+0x16C8 are not touched by this body.

Carried from donor source (lead, not BFME 1 proof): Zero Hour GameLOD.cpp init
flow and member names (m_lodPresets, m_benchProfiles, m_memPassed, ...); Open-BFME-2
73898a9634 Code/GameEngine/Source/Common/GameLODManagerInit.cpp split-unit shape.

Name corrections versus the 2026-09-30 bank: the bank's whole-class view put
ZH names (m_audioLOD, m_numParticleGenerations, m_dynamicParticleSkipMask) on
offsets this body does not prove, so the new unit names only what it touches by
offset (m_field16C4/16C8/16CC), and calls the two placeholder-named bodies by
their ledger/pin names until those rows are renamed.
