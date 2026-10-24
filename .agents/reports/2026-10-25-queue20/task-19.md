# Task 19: audio handle vector overflow — blocked

Queue rank 26, census e9a5ae5b4c. Three potential emitters were inspected: Common/INI/Rva000BDD20ParseAudioRefs.cpp, Common/Audio/AudioManagerFindAllAudioEventsOfType.cpp and GameLogic/Object/Behavior/SlowDeathBehavior_parseSound.cpp. The dedicated provider is Common/Rva000BD3B0VectorInsertOverflowBody.cpp, retail 0x000BD3B0, 328 bytes.

Tried the BFME2 declaration-only specialization technique from sibling revision f301d686c70c3e5fa0b51b342a2745f495b8a0b1, Code/Libraries/Source/WWVegas/WWLib/RvaHashResize00927DE0.cpp and commit e9d93338e0. It is inapplicable without caller reconstruction: all three existing matched callers fail. AudioManager's frame grows from 0x18 to 0x1c; SlowDeath's grows from 0x08 to 0x0c and saves an extra register. Empty-tag storage and initialization appear in the edited callers; associated instruction and call offsets shift. The INI parser likewise changes its frame/instruction layout. This is a real byte mismatch, not a reason to enlarge row extents or alter pins.

All attempted source changes were reverted. Scoped builds of all three original callers pass after restoration. No source repair landed for this task. This commit retains only the independently reproduced blocker evidence.

Next direction: retain the native helper's visible empty-tag semantics and reconcile its own code generation with retail. The dedicated 328-byte body calls the proven construction and destroy-range routes, whereas the competing generic template sees local refcount wrappers. Such a repair must independently preserve all three caller bodies and verify helper relocations. Do not repeat declaration-only suppression against unchanged inputs. No global linked-byte gain or conversion is claimed.
