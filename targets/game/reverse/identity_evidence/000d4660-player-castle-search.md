# Player search at 0x000D4660

The complete retail body spans 0x000D4660..0x000D46C4 (100 bytes).
Its final RET8 is at +0x61, followed by INT3 padding. The old 82-byte picker
extent stopped in the outgoing object lookup; the ledger already has the
correct 100-byte extent. No boundary or identity pin is added.

Matched CommandXlat.cpp and CommandXlatVoice.cpp callers declare
`Player::rva000D4660(bool,Object**) const`; the former passes the local player
from ThePlayerList+0xC and `(true,0)`. The lexical method name is unknown,
so the existing address-derived spelling is retained.

The retail body builds a 16-byte stack visitor record containing this player,
the low byte of the first argument, and two zero pointer fields. It passes
that record and callback VA 0x004D4500 to Player::iterateObjects through ILT
0x0002F1CB. The callback's complete 273-byte body reads this same record,
obtains a module using the literal "CastleBehavior", and updates the selected
Object and module fields. It treats the module's +0xA0 value as an object ID:
the consumer at +0x45 passes it to GameLogic::findObjectByID through ILT
0x0001F253. If that lookup fails, or no module was selected, the original
selected Object is returned. The optional output always receives that original
selection before the lookup. No module identity is inferred from equal bytes.

The callback keeps its existing anonymous `d_000d4500` ledger symbol. A typed
visitor cast expresses the independently decoded two-pointer cdecl call shape
without hardcoding a code address or adding a semantic pin. The iteration
body at 0x000CDCF0 calls the callback with those two arguments and ignores EAX;
the existing void-return ILT view at 0x0002F1CB is unchanged.

The preferred bank was 102 bytes, with an extra EAX-to-EDI move after the walk.
Using the real CastleBehavior pointer in the context preserves that result.
Exposing the genuine read-only lookup in GameLogicObjectLookup.h makes the
whole 100-byte caller exact, including all four relocation operands. The
82-byte lookup must also be verified independently in this TU; its authoritative
row remains GameLogicFindObjectByID.cpp. No duplicate lookup row is added.
