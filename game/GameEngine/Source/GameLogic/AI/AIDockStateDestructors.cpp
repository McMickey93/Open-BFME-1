// cl: /DNDEBUG /MD /EHsc
//
// Complete destructors of three AIDock move states (5 bytes each): one tail
// jump through ILT 0x0004AAF7 into ~AIInternalMoveToState with no vptr
// re-seat of their own, as AIDockMoveToEntryStateDestructor.cpp. Each is
// reached from its class's ??_G (still a generated row) through the ILT
// that ilt_oracle CONFIRMS for the name:
//   0x0014F410 ~AIDockApproachState   ILT 0x000425C8
//   0x0014F600 ~AIDockMoveToDockState ILT 0x00011658
//   0x0014F700 ~AIDockMoveToExitState ILT 0x00015979
// novtable reproduces the missing re-seat; it lives apart from the ??_G TU
// because a novtable class there would no longer emit its vftable and ??_G.

class AIInternalMoveToState
{
public:
	virtual ~AIInternalMoveToState();
};

class __declspec(novtable) AIDockApproachState : public AIInternalMoveToState
{
public:
	virtual ~AIDockApproachState();
};

AIDockApproachState::~AIDockApproachState()
{
}

class __declspec(novtable) AIDockMoveToDockState : public AIInternalMoveToState
{
public:
	virtual ~AIDockMoveToDockState();
};

AIDockMoveToDockState::~AIDockMoveToDockState()
{
}

class __declspec(novtable) AIDockMoveToExitState : public AIInternalMoveToState
{
public:
	virtual ~AIDockMoveToExitState();
};

AIDockMoveToExitState::~AIDockMoveToExitState()
{
}
