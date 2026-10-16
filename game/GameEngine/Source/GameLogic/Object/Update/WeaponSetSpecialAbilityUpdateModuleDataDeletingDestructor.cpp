// cl: /DNDEBUG /MD /EHsc

// Open-BFME5: WeaponSetSpecialAbilityUpdateModuleData scalar-deleting
// destructor at retail RVA 0x0026DD90 (30 bytes).  Its matched constructor
// at 0x0026DC20 installs module-data vtable 0x010B8DF0 after the shared
// SpecialAbilityUpdateModuleData base construction.  The wrapper's call is
// the shared base destructor ILT 0x0001980D, establishing this derived
// module-data identity.


class SpecialAbilityUpdateModuleData
{
public:
	virtual ~SpecialAbilityUpdateModuleData();
};

// The destructor is implicit: retail ~WeaponSetSpecialAbilityUpdateModuleData
// at 0x0026DDC0 (own ILT 0x000466DC) is a bare tail jump to
// SpecialAbilityUpdateModuleData::~SpecialAbilityUpdateModuleData (ILT
// 0x0001980D) with no vptr reset, the shape VC7.1 gives an implicit virtual
// destructor; both ILTs are ilt_oracle CONFIRMED exact.
class WeaponSetSpecialAbilityUpdateModuleData : public SpecialAbilityUpdateModuleData
{
};

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_WeaponSetSpecialAbilityUpdateModuleData_Vtable() { WeaponSetSpecialAbilityUpdateModuleData value; }
