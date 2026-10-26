// cl: /DNDEBUG /MD /EHsc
// Open-BFME5: GiveUpgradeUpdate module-data and instance factories.

class Module;
class Thing;
class INI;
class ModuleData;

void *__cdecl operator new(unsigned int);
void __cdecl operator delete(void *);

class GiveUpgradeUpdateModuleData
{
public:
	GiveUpgradeUpdateModuleData();
	virtual ~GiveUpgradeUpdateModuleData();

private:
	unsigned char m_pad[0x270];
};

class MultiIniFieldParse;

// Retail's module-data factories reach INI through initFromINIMultiProc
// (0x00852130), which takes the class's buildFieldParse proc; the
// FieldParse-table overload this TU used to name lives at 0x008520A0.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/INI.h
class INI
{
public:
	void initFromINIMultiProc(void *what,
		void (__cdecl *buildFieldParse)(MultiIniFieldParse &));
};

// The pushed immediate is 0x00410CEE = the five-byte ILT thunk at 0x00010CEE,
// which chains to the GiveUpgradeUpdate field-parse builder, the matched
// address-derived ?buildFieldParse@Rva0025D970@@SAXAAVWideMulti@@@Z (body
// 0x0025D970 in game/GameEngine/Source/Common/WideBuildFieldParse.cpp).
// Naming that defined builder lets the reference link; its WideMulti
// receiver spelling is the matched row's, so the proc is cast to the
// initFromINIMultiProc parameter type (no code: push offset either way).
class WideMulti;
class Rva0025D970
{
public:
	static void buildFieldParse(WideMulti &);
};
typedef void (__cdecl *GiveUpgradeUpdateBuildFieldParse)(MultiIniFieldParse &);

class GiveUpgradeUpdate
{
public:
	GiveUpgradeUpdate(Thing *, const ModuleData *);
	static ModuleData *friend_newModuleData(INI *ini);
	static Module *friend_newModuleInstance(Thing *, const ModuleData *);

private:
	unsigned char m_pad[0xf0];
};

// ?friend_newModuleData@GiveUpgradeUpdate@@SAPAVModuleData@@PAVINI@@@Z
ModuleData *GiveUpgradeUpdate::friend_newModuleData(INI *ini)
{
	GiveUpgradeUpdateModuleData *data = new GiveUpgradeUpdateModuleData;
	if (ini)
		ini->initFromINIMultiProc(data,
			(GiveUpgradeUpdateBuildFieldParse)Rva0025D970::buildFieldParse);
	return (ModuleData *)data;
}

// ?friend_newModuleInstance@GiveUpgradeUpdate@@SAPAVModule@@PAVThing@@PBVModuleData@@@Z
Module *GiveUpgradeUpdate::friend_newModuleInstance(Thing *thing, const ModuleData *data)
{
	return (Module *)new GiveUpgradeUpdate(thing, data);
}
