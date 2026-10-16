// cl: /DNDEBUG /MD /EHsc

// Open-BFME5: DualWeaponBehaviorModuleData default ctor.
// Layout: vtable@0, gap@4 (uninit), dword@8, byte@c, dword@10, byte@14, byte@15.

class DualWeaponBehaviorModuleData
{
public:
	DualWeaponBehaviorModuleData();
	virtual ~DualWeaponBehaviorModuleData();

private:
	unsigned int m_gap4;
	unsigned int m_u8;
	unsigned char m_useCloseRangeWhileMounted;
	unsigned char m_pad0d;
	unsigned char m_pad0e;
	unsigned char m_pad0f;
	unsigned int m_minimumSwitchTime;
	unsigned char m_useHordeRangeWeapon;
	unsigned char m_useRealVictimRange;
};

// ??0DualWeaponBehaviorModuleData@@QAE@XZ
DualWeaponBehaviorModuleData::DualWeaponBehaviorModuleData()
{
	m_u8 = 0;
	m_useCloseRangeWhileMounted = 0;
	m_minimumSwitchTime = 0;
	m_useHordeRangeWeapon = 0;
	m_useRealVictimRange = 0;
}
