// cl: /DNDEBUG /MD /EHsc
//
// These empty derived destructors reproduce six retail 30-byte scalar-
// deleting wrappers. Matched constructors install the dedicated vtables
// whose slot-zero ILTs identify each wrapper.

// Retail's own StateMachine scalar-deleting destructor is
// ??1StateMachine@@MAE@XZ (game/GameEngine/Source/Common/StateMachineDestructorThunk.cpp),
// i.e. a PROTECTED virtual destructor.  Spelled public here the reference would
// never link, so keep the retail access specifier.
class StateMachine
{
protected:
	virtual ~StateMachine();
};

#define PUBLIC_STATE_MACHINE_DTOR(name) \
	class name : public StateMachine \
	{ \
	public: \
		virtual ~name() {} \
	}; \
	void force##name##DeletingDestructor() \
	{ \
		name value; \
	}

PUBLIC_STATE_MACHINE_DTOR(AttackMeleeStateMachine)
PUBLIC_STATE_MACHINE_DTOR(AttackFireWhileMovingMachine)
PUBLIC_STATE_MACHINE_DTOR(AttackFireWhileChargingMachine)
PUBLIC_STATE_MACHINE_DTOR(BackAwayAndCowerStateMachine)

// 0x0016E630 is AttackContesterStateMachine's scalar-deleting destructor: slot
// zero of vtable 0x01097310 (installed by its constructor 0x00171B40, name
// getter "AttackContesterStateMachine") reaches it; its destructor is protected
// (ILT oracle confirms ??_G...@@MAE and ??1...@@MAE, ILT 0x0001BD65).
class AttackContesterStateMachine : public StateMachine
{
	friend void forceAttackContesterStateMachineDeletingDestructor();

protected:
	virtual ~AttackContesterStateMachine();
};

void forceAttackContesterStateMachineDeletingDestructor()
{
	AttackContesterStateMachine value;
}

class AIAttackThenIdleStateMachine : public StateMachine
{
	friend void forceAIAttackThenIdleStateMachineDeletingDestructor();

protected:
	virtual ~AIAttackThenIdleStateMachine();
};

void forceAIAttackThenIdleStateMachineDeletingDestructor()
{
	AIAttackThenIdleStateMachine value;
}
