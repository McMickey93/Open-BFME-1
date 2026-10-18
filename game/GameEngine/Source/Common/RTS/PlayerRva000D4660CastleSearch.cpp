// cl: /DNDEBUG /DWIN32 /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS /Igame/GameEngine/Source
// stlport
// Retail RVA 0x000D4660, 100 bytes. CommandXlat callers establish Player and
// the bool/Object** ABI. The callback remains named only by its address.
// Evidence: targets/game/reverse/identity_evidence/000d4660-player-castle-search.md.
class Object;

#define BFME_GAMELOGIC_LOOKUP_VISIBLE
#include "Common/Thing/GameLogicObjectLookup.h"
extern GameLogic *TheBfmeGameLogic;

// The visitor obtains this module using the literal "CastleBehavior" and
// reads its owner object ID at +0xA0. The full module layout is not needed.
class CastleBehavior
{
public:
 char m_unreconstructed00[0xA0];
 int m_ownerID;
};
// The frozen callback row has an address-only void() symbol. Its actual
// visitor ABI is two cdecl pointer arguments; Player ignores its return.
void d_000d4500();
class Player;
// Retail passes the callback at RVA 0x000D4500 (VA 0x004D4500).
// Its original method name is unresolved, so this source keeps the address.
typedef void (*Rva000D4500Visitor)(Object *, void *);
struct Rva000D4660VisitContext
{
	const Player *player;
	bool flag;
	Object *chosen;
	CastleBehavior *special;
};

class Player
{
public:
	void iterateObjects(Rva000D4500Visitor visitor, void *data) const;
	Object *rva000D4660(bool flag, Object **out) const;
};

Object *Player::rva000D4660(bool flag, Object **out) const
{
	Rva000D4660VisitContext info;
	info.player = this;
	info.flag = flag;
	info.chosen = 0;
	info.special = 0;
	iterateObjects(reinterpret_cast<Rva000D4500Visitor>(&d_000d4500), &info);
	Object *chosen = info.chosen;
	if (out)
		*out = chosen;
	if (info.special) {
		Object *special = TheBfmeGameLogic->findObjectByID(info.special->m_ownerID);
		if (special)
			return special;
	}
	return chosen;
}
