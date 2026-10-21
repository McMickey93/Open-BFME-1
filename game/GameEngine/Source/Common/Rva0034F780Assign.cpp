// cl: /O2 /Ob0
// ObjectTypes::operator=, retail 0x0034F780 (39 bytes): copies the list name
// and the object-type vector. Open-BFME-2's matched ObjectTypes::operator= is
// byte-identical and BFME1's ILT slot confirms the decoration.

#include "../../../Libraries/Source/WWVegas/WWLib/string_base.h"

class Rva0076F980Mid
{
public:
	Rva0076F980Mid &operator=(const Rva0076F980Mid &other);

private:
	int m_00;
	int m_04;
	int m_08;
};

void j_00007a63();

// Keep the target's member-call ABI while referring to its recorded thunk name.
union Rva0076F980MidAssign
{
	void (*function)(void);
	Rva0076F980Mid &(Rva0076F980Mid::*member)(const Rva0076F980Mid &);
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/ObjectTypes.h
class ObjectTypes
{
	virtual void handle();
	StringBase<char> m_listName;		// +0x04
	Rva0076F980Mid m_objectTypes;		// +0x08

public:
	ObjectTypes &operator=(const ObjectTypes &that);
};

ObjectTypes &ObjectTypes::operator=(const ObjectTypes &that)
{
	m_listName.set(that.m_listName);
	Rva0076F980MidAssign assign;
	assign.function = &j_00007a63;
	(m_objectTypes.*assign.member)(that.m_objectTypes);
	return *this;
}
