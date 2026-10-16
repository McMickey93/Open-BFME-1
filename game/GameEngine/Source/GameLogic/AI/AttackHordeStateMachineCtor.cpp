// cl: /DNDEBUG /MD /EHsc /Iinputs/reference/shims/stringinline

#include "StringInline.h"

class Object;
class State;
class AIAttackState;
struct StateConditionInfo;
class NotifyWeaponFiredInterface;

bool __cdecl rva00171b20FlagCheck(const void *object);
extern void d_0016af70();

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/StateMachine.h
class StateMachine
{
public:
	StateMachine( Object *owner, AsciiString name, bool flag );

protected:
	// retail declares the virtual destructor protected; that access level is
	// part of the mangled name the compiler-emitted cleanup path calls.
	virtual ~StateMachine();
	void defineState( unsigned int id, State *state,
		unsigned int successID, unsigned int failureID,
		const StateConditionInfo *conditions );
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/StateMachine.h
class State
{
public:
	State( StateMachine *machine, AsciiString name );
	virtual ~State();

private:
	unsigned char m_head[ 0x20 ];
};

typedef bool (*Rva00171B40StateTransFunc)( State *state,
	void *userData );

struct StateConditionInfo
{
	Rva00171B40StateTransFunc test;
	unsigned int toStateID;
	void *userData;

	StateConditionInfo( Rva00171B40StateTransFunc t, unsigned int id,
		void *ud )
		: test( t ), toStateID( id ), userData( ud )
	{
	}
};

class Rva00171B40AIAttackFireWeaponState : public State
{
public:
	Rva00171B40AIAttackFireWeaponState(
		StateMachine *machine, NotifyWeaponFiredInterface *notify );

private:
	NotifyWeaponFiredInterface *m_notify;
	bool m_finished;
};

// ??0Rva00171B40AIAttackFireWeaponState@@QAE@XZ absent-from-retail
Rva00171B40AIAttackFireWeaponState::Rva00171B40AIAttackFireWeaponState(
StateMachine *machine, NotifyWeaponFiredInterface *notify )
	: State( machine, AsciiString( "AIAttackFireWeaponState" ) ),
	  m_notify( notify ),
	  m_finished( false )
{
}

class Rva00171B40AIWaitUntilFinishedFiringState : public State
{
public:
	Rva00171B40AIWaitUntilFinishedFiringState(
		StateMachine *machine );
};

Rva00171B40AIWaitUntilFinishedFiringState::
	Rva00171B40AIWaitUntilFinishedFiringState(
		StateMachine *machine )
	: State( machine,
		AsciiString( "AIWaitUntilFinishedFiringState" ) )
{
}

// AttackContesterStateMachine (identity_evidence/0x00171b40-contester-identity.md):
// the factory's ATTACK_MACHINE_HORDE_CONTESTER case builds it as
// "AIAttackContesterMachine"; the vtable this constructor installs, 0x01097310,
// has the name getter 0x0016AC50 returning "AttackContesterStateMachine", and
// its protected complete destructor is 0x0016AC40 (ILT oracle: MAE).
class AttackContesterStateMachine : public StateMachine
{
public:
	AttackContesterStateMachine(
		Object *owner, AIAttackState *attack, AsciiString name );

protected:
	virtual ~AttackContesterStateMachine();
};

// ??0AttackContesterStateMachine@@QAE@PAVObject@@PAVAIAttackState@@VAsciiString@@@Z
AttackContesterStateMachine::AttackContesterStateMachine(
	Object *owner, AIAttackState *attack, AsciiString name )
: StateMachine( owner, name, false )
{
	static const StateConditionInfo conditions[] =
	{
		StateConditionInfo(
			(Rva00171B40StateTransFunc)rva00171b20FlagCheck, 0x270f, 0 ),
		StateConditionInfo(
			(Rva00171B40StateTransFunc)d_0016af70, 0x270f, (void *)2 ),
		StateConditionInfo( 0, 0, 0 )
	};

	Rva00171B40AIAttackFireWeaponState *fire =
		new Rva00171B40AIAttackFireWeaponState(
			this, attack ? (NotifyWeaponFiredInterface *)((char *)attack + 0x24) : 0 );
	defineState( 0x1f4, (State *)fire, 0x1f5, 0x270f,
		(const StateConditionInfo *)conditions );

	Rva00171B40AIWaitUntilFinishedFiringState *wait =
		new Rva00171B40AIWaitUntilFinishedFiringState( this );
	defineState( 0x1f5, (State *)wait, 0x1f4, 0x270f,
		(const StateConditionInfo *)conditions );
}
