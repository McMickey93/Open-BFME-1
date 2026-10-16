// cl: /DNDEBUG /MD /EHsc
//
// Complete destructors of five SupplyTruck state-machine states (5 bytes
// each): one tail jump through ILT 0x00016725 into ~State with no vptr
// re-seat of their own. Each is the body behind the ILT its class's ??_G
// calls, and ilt_oracle CONFIRMS the ??1 name at that ILT:
//   0x002C6A50 ~RegroupingState      ILT 0x00042C80
//   0x002C6A90 ~DockingState         ILT 0x0002BD7D
//   0x002C6AD0 ~HarvestingState      ILT 0x0004862B
//   0x002C6C70 ~SupplyTruckBusyState ILT 0x0000AB00
//   0x002C6CB0 ~SupplyTruckIdleState ILT 0x00036976
// novtable reproduces the missing re-seat (see
// AI/AIDockMoveToEntryStateDestructor.cpp); it keeps this TU from emitting
// the vftables, so the ??_G wrappers cannot live here.

class State
{
public:
	virtual ~State();
};

#define BFME_STATE_TAIL_DTOR( NAME )                                          \
	class __declspec(novtable) NAME : public State                            \
	{                                                                         \
	public:                                                                   \
		virtual ~NAME();                                                      \
	};                                                                        \
	NAME::~NAME()                                                             \
	{                                                                         \
	}

BFME_STATE_TAIL_DTOR( RegroupingState )
BFME_STATE_TAIL_DTOR( DockingState )
BFME_STATE_TAIL_DTOR( HarvestingState )
BFME_STATE_TAIL_DTOR( SupplyTruckBusyState )
BFME_STATE_TAIL_DTOR( SupplyTruckIdleState )
