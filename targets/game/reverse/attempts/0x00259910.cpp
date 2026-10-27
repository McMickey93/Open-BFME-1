// ?doSpecialPower@CombineHordeSpecialPower@@UAEXI@Z
// partial score=0.9568 date=2026-10-27
// CombineHordeSpecialPower::doSpecialPower, retail 0x00259910..0x00259AC8 (440 B):
// slot 11 of the SpecialPowerModuleInterface table 0x010B3D58, which the
// matched CombineHordeSpecialPower constructor 0x002596F0 stores at +0x10.
// The body is reached only through ILT 0x0003EE9B; Object::doSpecialPower
// (0x001C3790) calls slot 11 as doSpecialPower.
// Evidence: targets/game/reverse/identity_evidence/00259910-combinehorde-dospecialpower.md
// Filter and iterator views follow GrabPassengerSpecialPowerDoSpecialPower.cpp
// and VeterancyCrateCollideExecute.cpp (same 0x009F2960 iterate call).
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/bfmekindof /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib
// stlport

#define _STLP_USE_STATIC_LIB 1
#define _STLP_NO_EXCEPTIONS 1
#define BFME_STLP_NODE_ALLOC 1
#include "PreRTS.h"
#include "Common/BitFlags.h"
#include <vector>

class Object;
class Player;

typedef BitFlags<192> Rva00259910KindOfMask;

class PartitionFilter
{
public:
	PartitionFilter() : m_next(0) {}
	virtual ~PartitionFilter() {}
	virtual Bool allow(Object *) = 0;
	virtual Int getPlayerMask();
	PartitionFilter *link(PartitionFilter *next);
	PartitionFilter *m_next;
};

// Retail table 0x01085DD0, one Object pointer after the base head.
class Rva0025ED50ObjectFilter : public PartitionFilter
{
public:
	Rva0025ED50ObjectFilter(Object *object) : m_object(object) {}
	virtual ~Rva0025ED50ObjectFilter() {}
	virtual Bool allow(Object *);
	Object *m_object;
};

// Retail table 0x010B243C, one 24-byte kind-of mask after the base head.
class Rva0025F2D0KindOfAnyFilter : public PartitionFilter
{
public:
	Rva0025F2D0KindOfAnyFilter(const Rva00259910KindOfMask &mask)
		: m_mask(mask) {}
	virtual ~Rva0025F2D0KindOfAnyFilter() {}
	virtual Bool allow(Object *);
	Rva00259910KindOfMask m_mask;
};

// Retail table 0x01083B80, no fields after the base head.
class Rva0025ED50RootFilter : public PartitionFilter
{
public:
	Rva0025ED50RootFilter() {}
	virtual ~Rva0025ED50RootFilter() {}
	virtual Bool allow(Object *);
};

// Retail table 0x0109688C: player +0x08, match flag +0x0C.
class PartitionFilterPlayer : public PartitionFilter
{
public:
	PartitionFilterPlayer(const Player *player, Bool match)
		: m_player(player), m_match(match) {}
	virtual ~PartitionFilterPlayer() {}
	virtual Bool allow(Object *);
	const Player *m_player;
	Bool m_match;
};

struct Rva00259910Item
{
	Object *m_object;
	float m_distance;
};
struct Rva00259910Payload
{
	std::vector<Rva00259910Item> m_items;
	Rva00259910Item *m_cursor;
	int m_refCount;
};
struct BfmeWideResult
{
	Rva00259910Payload *m_value;
	~BfmeWideResult()
	{
		--m_value->m_refCount;
		if (m_value->m_refCount == 0)
			delete m_value;
	}
	Object *next()
	{
		if (m_value->m_cursor == m_value->m_items.end())
			return 0;
		return (m_value->m_cursor++)->m_object;
	}
};
class BfmeWideForwardC
{
public:
	// RVA 0x009F2960 owns the five raw-word call signature.
	BfmeWideResult bfmeForwardWideC(int, int, int, int, int);
};
class PartitionManager;
extern PartitionManager *ThePartitionManager;

class AICommandInterface
{
public:
	void aiBfmeCommand45(Object *target, CommandSourceType commandSource);
};

class Rva00259910AI
{
public:
	char m_head[0x20];
	AICommandInterface m_commands;
};

// Interface reached through the address-derived Object accessor at 0x001BFE20;
// slot 27 takes the special power's owner.
class Rva00259910Interface
{
public:
	virtual void slot00(); virtual void slot01(); virtual void slot02();
	virtual void slot03(); virtual void slot04(); virtual void slot05();
	virtual void slot06(); virtual void slot07(); virtual void slot08();
	virtual void slot09(); virtual void slot10(); virtual void slot11();
	virtual void slot12(); virtual void slot13(); virtual void slot14();
	virtual void slot15(); virtual void slot16(); virtual void slot17();
	virtual void slot18(); virtual void slot19(); virtual void slot20();
	virtual void slot21(); virtual void slot22(); virtual void slot23();
	virtual void slot24(); virtual void slot25(); virtual void slot26();
	virtual Bool slot27(Object *owner);
};

class Object
{
public:
	Player *getControllingPlayer() const;
	void *unidentified_001BFE20() const;
	unsigned char m_00_to_38[0x38];
	Coord3D m_position;
	unsigned char m_44_to_1A4[0x1A4 - 0x44];
	UnsignedInt m_disabledMask;
	unsigned char m_1A8_to_204[0x204 - 0x1A8];
	Rva00259910AI *m_ai;
};

struct Rva00259910Data
{
	unsigned char m_00_to_210[0x210];
	Real m_range;
};

class CombineHordeSpecialPower
{
public:
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual void slot0C(); virtual void slot10(); virtual void slot14();
	virtual void slot18(); virtual void slot1C(); virtual void slot20();
	virtual void slot24(); virtual void slot28();
	virtual void doSpecialPower(UnsignedInt options);
	virtual void slot30(); virtual void slot34(); virtual void slot38();
	virtual void slot3C();
	virtual void startPowerRecharge();
	Object *getObject() const
	{
		return *reinterpret_cast<Object *const *>(
			reinterpret_cast<const unsigned char *>(this) - 8);
	}
	const Rva00259910Data *getData() const
	{
		return *reinterpret_cast<Rva00259910Data *const *>(
			reinterpret_cast<const unsigned char *>(this) - 12);
	}
};

void CombineHordeSpecialPower::doSpecialPower(UnsignedInt options)
{
	Object *object = getObject();
	if (object->m_disabledMask)
		return;

	startPowerRecharge();

	Rva00259910KindOfMask mask(Rva00259910KindOfMask::kInit, 108);
	BfmeWideResult result = ((BfmeWideForwardC *)ThePartitionManager)->bfmeForwardWideC(
		(int)&object->m_position, *reinterpret_cast<const int *>(&getData()->m_range), 0,
		(int)PartitionFilterPlayer(object->getControllingPlayer(), true).link(
			Rva0025ED50RootFilter().link(
				Rva0025F2D0KindOfAnyFilter(mask).link(
					&Rva0025ED50ObjectFilter(object)))),
		1);
	while (Object *other = result.next())
	{
		Rva00259910Interface *iface =
			(Rva00259910Interface *)other->unidentified_001BFE20();
		if (!iface)
			continue;
		if (!iface->slot27(object))
			continue;
		object->m_ai->m_commands.aiBfmeCommand45(other, CMD_FROM_AI);
		break;
	}
}
