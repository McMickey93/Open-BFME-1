// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: public scalar-deleting destructor for HordeGarrisonContain.
// The exact constructor at 0x00248F90 installs dedicated vtable 0x010AFDC0;
// slot zero routes through ILT 0x00006528 to this 30-byte wrapper, whose
// complete destructor is reached through ILT 0x00038622.

// The destructor is implicit: retail ~HordeGarrisonContain at 0x0021A2B0 (own ILT 0x00038622) is a
// bare tail jump to GarrisonContain::~GarrisonContain (ILT 0x00037A24) with no vptr reset, the
// shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class GarrisonContain
{
public:
	virtual ~GarrisonContain();
};

class HordeGarrisonContain : public GarrisonContain
{
};

void forceHordeGarrisonContainDeletingDestructor()
{
	HordeGarrisonContain value;
}
