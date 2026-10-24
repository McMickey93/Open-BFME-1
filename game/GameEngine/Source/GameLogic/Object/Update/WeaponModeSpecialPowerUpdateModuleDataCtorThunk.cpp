// cl: /DNDEBUG /MD /GX- /O2 /Ob2

// Open-BFME5: WeaponModeSpecialPowerUpdateModuleData ctor
// Retail: base, xor eax, vtbl, zeros +0x1d0/+0x1d4, +0x1d8=3, zero +0x1dc twice.
// Volatile stores preserve order under MSVC 7.1.

class WeaponModeSpecialPowerUpdateModuleDataBase
{
public:
	WeaponModeSpecialPowerUpdateModuleDataBase();
	virtual void weaponModeModuleDataBaseAnchor();

private:
	unsigned char m_pad[0x1CC];
};

// Retail table at VA 0x010C5510: 17 slots, ending before 0x010C5554.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?j_00017cec@@YAXXZ")();
extern "C" void __identifier("?j_00027f5c@@YAXXZ")();
extern "C" void __identifier("?j_000148df@@YAXXZ")();
extern "C" void __identifier("?j_0002e5d7@@YAXXZ")();
extern "C" void __identifier("?j_00015b77@@YAXXZ")();
extern "C" void __identifier("?j_000294a6@@YAXXZ")();
extern "C" void __identifier("?j_0002a03b@@YAXXZ")();
extern "C" void __identifier("?j_00020bee@@YAXXZ")();
extern "C" void __identifier("?j_0000b9f6@@YAXXZ")();
extern "C" void __identifier("?j_00013624@@YAXXZ")();
extern "C" void __identifier("?j_0004b547@@YAXXZ")();
extern "C" void __identifier("?j_0000558d@@YAXXZ")();
extern "C" void __identifier("?j_000273b8@@YAXXZ")();
extern "C" void __identifier("?j_0003308c@@YAXXZ")();
extern "C" void __identifier("?j_0000adf8@@YAXXZ")();
extern "C" void __identifier("?j_0001794a@@YAXXZ")();
extern "C" void __identifier("?j_0003099f@@YAXXZ")();
extern "C" void *WeaponModeSpecialPowerUpdateModuleData_vtbl[] = {
    reinterpret_cast<void *>(&__identifier("?j_00017cec@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00027f5c@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_000148df@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0002e5d7@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00015b77@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_000294a6@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0002a03b@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00020bee@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0000b9f6@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00013624@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0004b547@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0000558d@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_000273b8@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0003308c@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0000adf8@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0001794a@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0003099f@@YAXXZ")),
};

class __declspec(novtable) WeaponModeSpecialPowerUpdateModuleData
	: public WeaponModeSpecialPowerUpdateModuleDataBase
{
public:
	WeaponModeSpecialPowerUpdateModuleData();

private:
	unsigned int m_1d0;
	unsigned int m_1d4;
	unsigned int m_1d8;
	unsigned int m_1dc;
};

// ??0WeaponModeSpecialPowerUpdateModuleData@@QAE@XZ
WeaponModeSpecialPowerUpdateModuleData::WeaponModeSpecialPowerUpdateModuleData()
{
	*reinterpret_cast<char *volatile *>(this) =
		reinterpret_cast<char *>(WeaponModeSpecialPowerUpdateModuleData_vtbl);
	*reinterpret_cast<unsigned int volatile *>(&m_1d0) = 0;
	*reinterpret_cast<unsigned int volatile *>(&m_1d4) = 0;
	*reinterpret_cast<unsigned int volatile *>(&m_1d8) = 3;
	*reinterpret_cast<unsigned int volatile *>(&m_1dc) = 0;
	*reinterpret_cast<unsigned int volatile *>(&m_1dc) = 0;
}
