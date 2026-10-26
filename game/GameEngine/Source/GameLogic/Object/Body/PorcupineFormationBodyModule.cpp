// cl: /DNDEBUG /MD /EHsc
// Retire ??_7PorcupineFormationBodyModule@@6BObjectModule@@@: use ??_7PorcupineFormationBodyModule@@6BBehaviorModule@@@

class Thing;
class ModuleData;
class DamageInfo;
class BodyModuleInterface;

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Module/BehaviorModule.h
class BehaviorModule
{
public:
	virtual void behaviorModuleAnchor();

private:
	unsigned char m_data[8];
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Module/BehaviorModule.h
class BehaviorModuleInterface
{
public:
	virtual BodyModuleInterface *getBody() = 0;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Module/BodyModule.h
class BodyModuleInterface
{
public:
	virtual void attemptDamage(DamageInfo *damageInfo) = 0;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Module/ActiveBody.h
class ActiveBody : public BehaviorModule,
	public BehaviorModuleInterface,
	public BodyModuleInterface
{
public:
	ActiveBody( Thing *thing, const ModuleData *moduleData );
	virtual ~ActiveBody();
};

class PorcupineFormationBodyModule : public ActiveBody
{
public:
	PorcupineFormationBodyModule( Thing *thing, const ModuleData *moduleData );
	virtual void attemptDamage(DamageInfo *damageInfo);
protected:
	virtual ~PorcupineFormationBodyModule();
};

PorcupineFormationBodyModule::PorcupineFormationBodyModule(
	Thing *thing, const ModuleData *moduleData )
	: ActiveBody( thing, moduleData )
{
}

PorcupineFormationBodyModule::~PorcupineFormationBodyModule()
{
}
