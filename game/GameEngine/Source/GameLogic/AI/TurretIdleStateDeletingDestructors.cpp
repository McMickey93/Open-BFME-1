// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructors for two pool-backed turret states.
// Exact named constructors install their dedicated vtables and the slot-zero
// ILTs route to these 30-byte wrappers.
//
// Each wrapper calls its destructor through an ILT (0x0003F6AC, 0x0000F425;
// ilt_oracle CONFIRMED exact) rather than inlining it.  Both destructors are
// implicit: retail 0x0018E550 and 0x0018E590 are a bare tail jump to
// State::~State (ILT 0x00016725, ilt_oracle CONFIRMED exact) with no vptr
// reset, which a user-declared destructor would emit.

class State
{
public:
	virtual ~State();
};

class TurretAIIdleState : public State
{
private:
	friend void forceTurretAIIdleStateDeletingDestructor();
};

class TurretAIIdleScanState : public State
{
private:
	friend void forceTurretAIIdleScanStateDeletingDestructor();
};

void forceTurretAIIdleStateDeletingDestructor() { TurretAIIdleState value; }
void forceTurretAIIdleScanStateDeletingDestructor() { TurretAIIdleScanState value; }
