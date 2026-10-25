# LivingWorldManager::rva0060f3c0

BFME 1 RVA `0x0060F3C0`, 184 bytes, no explicit arguments, this in ECX.
The matched `Rva003C2530Owner::prepare` at `0x003BCC70` loads the independently
identified `TheLivingWorldManager` singleton (`0x012F706C`) and invokes ILT
`0x00016DEC`, which jumps to this body. That proves class ownership, not the
old bank's inferred `playSound` name. Keep the address-derived member name.
The full body returns at +0xB7; INT3 begins at +0xB8. No adjacency-based extent
or second identity is claimed.

## Independently observed BFME 1 ABI and layout

* The receiver's +0x238 word is passed by address to ILT `0x00009250`, routing
  to the existing 145-byte constructor at `0x000B4780`. The +0x23C dword is its
  second stack argument, written by that constructor to event+0x2C; it sets
  event+0x28 to 1 and event+0x30 to 5 for nonzero owner IDs. The constructor
  returns with RET 8. The frame reserves 0x70 bytes for the event record.
* The queued +0x238 pointer is reread after the audio virtual call. Its nonnull
  value is released through KERNEL32 InterlockedDecrement at IAT VA 0x01358E54,
  taking pointee+4. A nonpositive count invokes deleting virtual slot zero
  with flag 1. The holder word is then cleared. It is a counted reference,
  **not** the canonical AsciiString storage claimed by the older bank.
  Counted/CountedPtr use the same measured contract as the existing
  AudioEventRTSCopyAndLifetime.cpp definitions.
* The legacy constructor symbol spells its first argument AsciiString, but
  resolves to the different, inlined twin at 0x000B4690. The existing thin
  constructor row at 0x000B4780 has no directly declarable C++ constructor
  spelling. The improved bank uses a typed member call through existing
  `j_00009250`, with the independently observed thiscall/reference/owner ABI.
  It adds no symbol pin or alias. The stack AudioEventRTS is an opaque
  112-byte record; no private offsets inside it are read here.
* The call at +0x56 dispatches the established audio slot +0x44 with the stack
  record's address. The result is unused; the unsigned return and const record
  contract agree with the existing AudioManager view in LivingWorldSoundCopyCtor.
  The global is the independently identified TheAudio at VA 0x012ED668, owned by
  GameAudio.cpp, not the old bank's TheAudioClientUpdate alias.
* Event cleanup at +0x8E invokes ILT `0x00026F35` to the existing 162-byte
  complete destructor at `0x000B31F0`. Its body releases strings at +0x6C,
  +0x1C, +0x18, +0x14, counted reference +8, and string +4. This is the established
  QAE cleanup route; the UAE symbol at ILT 0x0002671F names a different body.
  The local declaration preserves the existing direct complete-cleanup ABI.
* The tail uses the canonical TheLivingWorldLogic at VA 0x012F1028, loads +0x28,
  sets its +0x10 byte to 1, then clears receiver+0x294. Fields without independent
  EA naming evidence remain offset-named. name_oracle has no witnessed manager
  layout. No field name is inferred from equal offsets in another executable.

## Compiler recovery and provenance

The old preferred bank reproduced 184 bytes / 9 relocations / 13 differing bytes,
all a callee-saved ESI/EDI exchange for holder address versus counted pointer.
BFME 2 revision `8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9`, docs/recipes.md and
reverse/attempt_support/damage507d84-recovery-20261022 supplied the new lead:
merged branches can affect allocation. BFME 2 has no native matching body for
this function, so it supplies a compiler technique only. It supplies no BFME 1
name, field layout, callee address, or placement.

Duplicating clear() in a switch first reduced the residue to two scratch-register
bytes. A meaningful guard, `switch (queued.isEmpty()) { case false:
queued.clear(); break; default: break; }`, eliminated the original register
mirror. With the legacy external constructor declaration a masked probe showed
zero differences, but the normal add_match gate correctly rejected its call:
the selected constructor resolved to 0x000B4690, whereas retail uses the outlined
constructor through ILT 0x00009250. This was a real callee mismatch, not a false
rejection; do not land the apparently exact legacy declaration.

The correctly routed candidate emits 184 bytes, nine relocations and six masked byte
differences (score 178/184 = 0.967391). explain_mismatch resolves the call through
0x00009250 and reports only register encoding differences: offsets +0x45,
+0x47, +0x4A, +0x57, +0x60 and +0x62. The vtable/stack-record temporaries use
EAX/EDX instead of EDX/EAX, and the decrement argument uses EAX instead of ECX.
Callee-saved holder/pointee registers now match. probe shape is 1.000.

The source has no artificial duplicate branch, volatile shaping, assembly,
raw bytes, new pins, or optimization override. The reconstructed game source
was restored after the attempt; this is not an accepted conversion. The candidate
is stronger than the previous 13-byte mirror and reconciles its fake string,
global aliases, imported function spelling and inferred member name.

Pre-commit name_regression refused the preferred-bank update: it reports seven
descriptive-to-placeholder regressions and no registered naming correction.
The refused preferred-file change was restored rather than bypass the check.
The improved source remains in the immutable alternative whose SHA256 is
2b3170dba817b184f665e9ace3a7618941e2341012ff2f04eb53ebc11c75b112;
re_attempts.log records the refusal. The existing preferred file is unchanged.

Private work: build/banked-audio-20261025. Tested guard variants, native counted
reference/import declarations, virtual/nonvirtual cleanup contexts, constructor
argument/return types and member-pointer initialization forms, owner/record/route
locals, audio receiver forms and rotation_sweep singles/pairs. All correctly
routed useful variants retain at least six differences. Free-function __thiscall
is rejected by MSVC 7.1 (C4234); do not repeat it. A virtual AudioEventRTS
destructor adds a different EH frame and is not the observed ABI. Changing
compiler flags was already exhausted in prior attempts. The next useful lever
must change the legitimate constructor-call lowering/allocation context without
selecting the wrong twin, rather than repeat local spellings.

Compiler: repository MSVC 7.1 defaults plus /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
and the existing WWLib ascii_string.h include. Diagnostic objects remained in
private build/experiments paths. The immutable attempt history retains the older
bank. Link preview remains UNKNOWN because the prepared census has unreadable
ledger objects/stale selections; no linked-byte claim is made.
