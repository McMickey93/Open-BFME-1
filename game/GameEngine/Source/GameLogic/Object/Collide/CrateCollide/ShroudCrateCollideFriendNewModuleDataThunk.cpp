// cl: /DNDEBUG /MD /EHsc
// Open-BFME5: ShroudCrateCollide::friend_newModuleData factory.

class INI;
class ModuleData;

void *__cdecl operator new(unsigned int);
void __cdecl operator delete(void *);

class MultiIniFieldParse;

// ShroudCrateCollide declares no module-data class of its own, so the object
// this factory builds is a plain CrateCollideModuleData: the module-data macro
// it inherits from CrateCollide (MAKE_STANDARD_MODULE_DATA_MACRO_ABC,
// upstream Common/Module.h) names clsmd = CrateCollideModuleData.  Retail
// agrees at 0x0011EDC0 -- 0x54 bytes, exactly the base, one call to its
// out-of-line constructor through ILT thunk 0x000441CA, and no vtable store
// after it -- so the type instantiated here is the base itself.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/Generals/Code/GameEngine/Include/GameLogic/Module/CrateCollide.h
class CrateCollideModuleData
{
public:
	CrateCollideModuleData();

private:
	virtual void bfmeVtableSlot00();

	unsigned char m_pad[0x50];
};

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

// Retail's second argument is the address of the module-data buildFieldParse
// proc, which rides the ILT thunk at VA 0x00412742; the reference spells the
// name the DIR32 ledger records there, _ShroudCrateCollideFieldParse.  The
// builder it reaches is ?buildFieldParse@CrateCollideModuleData@@SAXAAVMultiIniFieldParse@@@Z
// (matched body 0x00217AB0 in game/GameEngine/Source/Common/MidTableRegisterForwarders.cpp),
// shared with HealCrateCollide's factory, which pushes the same thunk.
extern "C" void __cdecl ShroudCrateCollideFieldParse(MultiIniFieldParse &parse);

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Module/ShroudCrateCollide.h
class ShroudCrateCollide
{
public:
	static ModuleData *friend_newModuleData(INI *ini);
};

// ?friend_newModuleData@ShroudCrateCollide@@SAPAVModuleData@@PAVINI@@@Z
ModuleData *ShroudCrateCollide::friend_newModuleData(INI *ini)
{
	CrateCollideModuleData *data = new CrateCollideModuleData;
	if (ini)
		ini->initFromINIMultiProc(data, ShroudCrateCollideFieldParse);
	return (ModuleData *)data;
}
