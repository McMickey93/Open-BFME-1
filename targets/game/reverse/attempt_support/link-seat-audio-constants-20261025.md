# Audio float operand gate-debt repair

Input BFME 1 revision: `8c1d5491f7af28bafc2096f49c7b1a6f058f062e`.
This follows the untested literal lead in `20261025-readonly-float-debt.md`.

The existing `AudioManager::init` row establishes the nonvirtual identity,
953-byte extent at RVA `0x006B8220`, and its separate translation unit.
The existing matched data rows independently establish readonly floats:
VA `0x0109F748`, bytes `00 00 40 3f`, is `0.75f`; VA `0x010B933C`,
bytes `cd cc 0c 3f`, is `0.55f`. Retail FLD operands at init+`0x24b`
and init+`0x226/0x26f/0x294/0x2b9` read those addresses. These are target
facts, not inferred channel defaults or names.

Five fallback expressions now use those literal values. The existing data
definitions remain byte-verified. Channel field accesses, locals, calls,
receiver layout, ABI and the existing unwind funclet are unchanged. No new
name, alias, pin, data row or registry entry is introduced. Comments spell
the two existing COFF owner names so the keyed debt test can locate this TU.

The original named operands failed the keyed tests against the already
recorded `__real@3f400000` and `__real@3f0ccccd` identities. Plain literals
retain exact bytes and use the verifier's constant operand checks instead.
Normal `./build.sh game/GameEngine/Source/Common/Audio/AudioManagerInit.cpp`
and both `repair_queue.py pass-test` commands pass: functions 2/2, data 7/7,
14 strings, five float constants, 18 DIR32 references, zero baselined body
findings. The tests delete exactly two exceptions: debt 992 -> 990.
No authored-C++ or linked-byte increase is claimed.

Read-only BFME 2 revision `e2fdc5620c5834c1c98de24aa3510d72e2cbcc69`
was searched for this unit and these operands. No corresponding donor
identity or applicable source repair was found; this change uses BFME 1
target and existing matched-data evidence.

## Other linking investigation in this session

The served BfmeConv1042 spelling repair was byte-exact in the caller (5/5)
and canonical provider (1/1), but live link verification was unknown with
539 unavailable or changed objects. The census-only 232-byte preview is
not a measured linking gain. The source was reverted and its synthetic
claim released. A local diagnostic patch remains at
`build/link-seat-20261025/conv1042-verified-caller.patch`; the source change
was only the receiver declaration/call from BfmeSub1042::bfmeSet1042 to
the existing Gen_00942BC0::process(void*, void*, void*) row. Retry only
after dependencies or the census change. The attempt log records the
independent callee ABI evidence and BFME 2 donor commit reviewed.
