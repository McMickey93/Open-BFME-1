// ?bfmeSetNeedsGateOpenRaw@Team@@QAEXHH@Z
// partial score=1.0 date=2026-10-18
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad
// stlport
// BFME Team::bfmeSetNeedsGateOpenRaw, retail RVA 0x000F1950.
// The Team keeps one object-ID set for gates that this team asks to stay open.
// A change in membership adjusts the matching GateOpenAndCloseBehavior request.

#define _STLP_NO_EXCEPTIONS 1
#define BFME_STLP_NODE_ALLOC 1
#define __PLACEMENT_VEC_NEW_INLINE
#include "Common/NameKeyGenerator.h"
#include <set>

typedef int Int;

// The set's key type is the enum the matched insert_unique (0x000EEC50) names.
enum Rva000EEC50Key { RVA000EEC50KEY_NONE };
typedef Rva000EEC50Key GateIDKey;
typedef _STL::set<GateIDKey> BfmeGateRequestSet;

extern NameKeyGenerator *TheNameKeyGenerator;

class Team;
class Module;
class Object
{
	friend class Team;
public:
	int getID() const;
protected:
	Module *findModule(NameKeyType key) const;
};

class GameLogic
{
public:
	Object *findObjectByID(Int id);
};

extern GameLogic *TheBfmeGameLogic;

class Module
{
public:
	virtual ~Module();
};

class GateOpenAndCloseBehaviorBase
{
public:
	virtual void slot00() = 0;
};

class Rva001FC440
{
public:
	void set(Int delta);
};
class GateOpenAndCloseBehavior : public GateOpenAndCloseBehaviorBase, public Module
{
};

class Team
{
private:
	unsigned char m_padding[0x104];
	BfmeGateRequestSet m_gateRequests;

public:
	void bfmeSetNeedsGateOpenRaw(Int gateID, Int needsOpen);
};

void Team::bfmeSetNeedsGateOpenRaw(Int gateID, Int needsOpen)
{
	BfmeGateRequestSet::const_iterator it = m_gateRequests.find((const GateIDKey &)gateID);
	const unsigned char needsOpenByte = *(const unsigned char *)&needsOpen;
	if (needsOpenByte == (it != m_gateRequests.end()))
		return;

	if (needsOpenByte)
		m_gateRequests.insert((const GateIDKey &)gateID);
	else
		m_gateRequests.erase(it);

	Object *gate = TheBfmeGameLogic->findObjectByID(gateID);
	if (gate == 0)
		return;

	static NameKeyType gateBehaviorKey =
		TheNameKeyGenerator->nameToKey("GateOpenAndCloseBehavior");
	GateOpenAndCloseBehavior *behavior =
		static_cast<GateOpenAndCloseBehavior *>(gate->findModule(gateBehaviorKey));
	if (behavior != 0)
		((Rva001FC440 *)behavior)->set(needsOpenByte ? 1 : -1);
}

// try build/a1_f1.cpp

// try build/a1_f2.cpp
