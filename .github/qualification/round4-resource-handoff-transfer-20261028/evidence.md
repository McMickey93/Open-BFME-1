# Resource-bar canonical-owner binding: blocked, 2026-10-28

Selected by the linking queue: the undefined Glo012F1028 name in `Rva0058DBC0OwnerUpdate.cpp` (943 existing bytes, census a0940f921b).
BFME 1 revision: c2503fbc13389c06061ada96ec794b2d3339cbeb. Original source blob: a7431ee7e24059f018c432042c71072361f007cc.

The tracked data row and `LivingWorldLogic.cpp` prove one typed owner, `LivingWorldLogic *TheLivingWorldLogic`, at VA 0x012F1028 (four zero bytes). The EA subsystem literal/store and constructor/name-vtable witnesses are documented in that owner.
The trial replaces the pin-only external Glo spelling with this existing owner and casts each use to the unchanged local field view. No layout, address, pin, authority line or function row changes.

## Native evidence and remaining prerequisite

[Windows qualification 40669952535](https://github.com/McMickey93/Open-BFME-1/actions/runs/40669952535), job 122753970736:
- Before: unmodified build.cmd passes both existing bodies (71 B/872 B) and the one 4 B data row.
- After: function-body comparison remains 2/2; data 1/1, four float constants and string-reference checks pass.
- The complete after-gate exits 1: at function offsets +0x1, +0x111, +0x251 and +0x284 the canonical data name is refused because VA 0x012F1028 is already recorded as Glo012F1028 plus 29 aliases.
- The structural COFF comparison was not reached. Link preview is UNKNOWN because the runner has no census index.

The companion patch is an unlanded trial. Game source retains the original Glo binding. No new C++ bytes or measured linked bytes are claimed.
Resume only after owner-approved canonical-data admission or a supported retirement of the retained aliases; do not edit the record by hand or bypass its sole writer.

BFME 2 donor review: revision 3459c2524cf56b2b06cac4217e8a839e3e26984e, `Code/GameEngine/Source/GameLogic/System/LivingWorld/LivingWorldLogic.cpp` owns the same typed global at its own VA 0x00DFEF10. Client units reuse it through local views. That corroborates the binding pattern; BFME 1 evidence establishes identity and address. No donor field offset or address was imported.
