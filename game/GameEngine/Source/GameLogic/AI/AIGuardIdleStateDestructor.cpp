// cl: /DNDEBUG /MD /EHsc
//
// AIGuardIdleState complete destructor at retail 0x0015D180 (5 bytes): one
// tail jump through ILT 0x00016725 into ~State with no vptr re-seat of its
// own. Its ??_G (0x0015D150, still a generated row) calls it
// through ILT 0x00048829, which ilt_oracle CONFIRMS for the name. novtable
// reproduces the missing re-seat (see AIDockMoveToEntryStateDestructor.cpp).

class State
{
public:
	virtual ~State();
};

class __declspec(novtable) AIGuardIdleState : public State
{
public:
	virtual ~AIGuardIdleState();
};

AIGuardIdleState::~AIGuardIdleState()
{
}
