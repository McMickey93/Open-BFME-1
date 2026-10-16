// cl: /DNDEBUG /MD /EHsc
// BFME-2 AutoFindHealingUpdateCtor.cpp at 2a0f7acb06 confirms trailing +0x20 zero.
// BFME-1 factory 0x00119780 and retail body 0x00281480..0x002814CD establish
// identity and layout; ProneUpdateConstructor.cpp supplies the BFME-1 inline
// three-base shape instead of BFME-2 UpdateModule call and dummy vtables.
class Thing;
class ModuleData;
class Object;

// upstream layout: GameLogic/Module/ObjectModule.h
class ObjectModule
{
public:
	ObjectModule(Thing *, const ModuleData *);
	virtual ~ObjectModule();

protected:
	void *m_moduleData;
	Object *m_object;
};

// upstream layout: GameLogic/Module/UpdateModule.h
class UpdateModuleInterface
{
public:
	virtual void updateInterfaceAnchor();
};

// upstream layout: GameLogic/Module/BehaviorModule.h
class BehaviorModuleInterface
{
public:
	virtual void behaviorInterfaceAnchor();
};

// upstream layout: GameLogic/Module/UpdateModule.h
// The three subobjects' names are opaque and keep the address of the table
// AutoFindHealingUpdate installs in each (0x010BB3C4 at +0x00, 0x010BB300 at
// +0x0C, 0x010BB2F0 at +0x10), so MSVC spells its vftables
// ??_7AutoFindHealingUpdate@@6BVa010BB3C4Subobject@@@ and so on. Retail proves
// which table sits at which offset, not what BFME called the base that
// introduced it, and MSVC 7.1 derives that part of the name from the whole
// declared hierarchy. novtable keeps the two interface subobjects from
// installing tables of their own, so the inlined base stores stay
// BehaviorModuleInterface's and UpdateModuleInterface's.
class Va010BB3C4Subobject : public ObjectModule
{
public:
	Va010BB3C4Subobject(Thing *thing, const ModuleData *moduleData) : ObjectModule(thing, moduleData) {}
};

class __declspec(novtable) Va010BB300Subobject : public BehaviorModuleInterface
{
};

class __declspec(novtable) Va010BB2F0Subobject : public UpdateModuleInterface
{
};

class UpdateModule : public Va010BB3C4Subobject,
	public Va010BB300Subobject,
	public Va010BB2F0Subobject
{
public:
	UpdateModule(Thing *thing, const ModuleData *moduleData)
		: Va010BB3C4Subobject(thing, moduleData),
		  m_nextCallFrameAndPhase(0), m_indexInLogic(-1), m_pad(-1)
	{
	}

private:
	unsigned int m_nextCallFrameAndPhase;
	int m_indexInLogic;
	int m_pad;
};

// upstream layout: GameLogic/Module/AutoFindHealingUpdate.h
class AutoFindHealingUpdate : public UpdateModule
{
public:
	AutoFindHealingUpdate(Thing *, const ModuleData *);

private:
	int m_nextScanFrames;
};

AutoFindHealingUpdate::AutoFindHealingUpdate(Thing *thing, const ModuleData *moduleData)
	: UpdateModule(thing, moduleData)
{
	// Retail writes the trailing field AFTER its own most-derived vftable batch
	// and before the epilogue, which a plain store would sink past the batch;
	// the volatile lvalue is what keeps it in the middle.
	*(volatile int *)&m_nextScanFrames = 0;
}
