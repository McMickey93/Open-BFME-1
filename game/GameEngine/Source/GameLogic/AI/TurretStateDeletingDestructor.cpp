// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for the abstract TurretState
// base at retail RVA 0x0018E4F0 (30 bytes). Its exact protected constructor at
// 0x0018D890 installs vtable 0x0109BC18, whose slot zero routes through ILT
// 0x0003BCDC; the wrapper calls the complete destructor via ILT 0x00032BF5.

// The destructors are implicit: retail ~TurretState at 0x0018D920 (own ILT 0x00032BF5) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class TurretState : public State
{
private:
	friend void forceTurretStateDeletingDestructor();
};

void forceTurretStateDeletingDestructor()
{
	TurretState value;
}
