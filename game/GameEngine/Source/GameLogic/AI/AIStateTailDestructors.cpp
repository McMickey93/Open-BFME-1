// cl: /DNDEBUG /MD /EHsc
//
// Protected complete destructors of two AI states (5 bytes each): one tail
// jump into the base destructor's ILT with no vptr re-seat of their own.
// Each is the body behind the ILT its matched ??_G calls, and ilt_oracle
// CONFIRMS the protected ??1 name at that ILT:
//   0x00171670 ~AIExitState                    ILT 0x0001B22F -> ~State 0x00016725
//   0x00185530 ~AIFollowWaypointPathExactState ILT 0x000078AB -> ~AIInternalMoveToState 0x0004AAF7
// novtable reproduces the missing re-seat (see
// AIDockMoveToEntryStateDestructor.cpp); it keeps this TU from emitting the
// vftables, so the ??_G wrappers stay in their own TUs.

class State
{
public:
	virtual ~State();
};

class AIInternalMoveToState
{
public:
	virtual ~AIInternalMoveToState();
};

class __declspec(novtable) AIExitState : public State
{
protected:
	virtual ~AIExitState();
};

AIExitState::~AIExitState()
{
}

class __declspec(novtable) AIFollowWaypointPathExactState : public AIInternalMoveToState
{
protected:
	virtual ~AIFollowWaypointPathExactState();
};

AIFollowWaypointPathExactState::~AIFollowWaypointPathExactState()
{
}
