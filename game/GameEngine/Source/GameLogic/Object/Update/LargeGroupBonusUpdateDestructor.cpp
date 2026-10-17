// cl: /DNDEBUG /MD /EHsc

class Module { public: virtual ~Module(); private: unsigned int m_storage[2]; };
class BehaviorModuleInterface { public: virtual void anchor(); };
class BehaviorModule : public Module, public BehaviorModuleInterface { public: virtual ~BehaviorModule() {} };
class UpdateModuleInterface { public: virtual void anchor(); };
class UpdateModule : public BehaviorModule, public UpdateModuleInterface
{
public:
	virtual ~UpdateModule() {}
private:
	unsigned int m_storage[3];
};
class LargeGroupBonusUpdateInterface { public: virtual void anchor(); };
class LargeGroupBonusUpdate : public UpdateModule, public LargeGroupBonusUpdateInterface
{
public:
	static void forceDestructorEmission();
protected:
	virtual ~LargeGroupBonusUpdate();
};

LargeGroupBonusUpdate::~LargeGroupBonusUpdate() {}

// ?forceDestructorEmission@LargeGroupBonusUpdate@@SAXXZ absent-from-retail
void LargeGroupBonusUpdate::forceDestructorEmission()
{
	// A local instance makes MSVC emit the protected scalar-deleting destructor.
	LargeGroupBonusUpdate value;
}

// Retail 0x00297480 (43 B) sits between this TU's LargeGroupBonusUpdate bodies and is
// the ZH getHUI/findCave module scan: walk Object+0x1F0 behavior modules and return the
// first non-null result of BehaviorModuleInterface slot +0x70. Its only use is inlined in
// retail 0x00297930, so the interface it returns is still unnamed.
class Object;
class Rva00297480Interface;

class Rva00297480ModuleInterface
{
public:
#define RVA00297480_SLOT(n) virtual void slot##n();
	RVA00297480_SLOT(00) RVA00297480_SLOT(01) RVA00297480_SLOT(02) RVA00297480_SLOT(03)
	RVA00297480_SLOT(04) RVA00297480_SLOT(05) RVA00297480_SLOT(06) RVA00297480_SLOT(07)
	RVA00297480_SLOT(08) RVA00297480_SLOT(09) RVA00297480_SLOT(10) RVA00297480_SLOT(11)
	RVA00297480_SLOT(12) RVA00297480_SLOT(13) RVA00297480_SLOT(14) RVA00297480_SLOT(15)
	RVA00297480_SLOT(16) RVA00297480_SLOT(17) RVA00297480_SLOT(18) RVA00297480_SLOT(19)
	RVA00297480_SLOT(20) RVA00297480_SLOT(21) RVA00297480_SLOT(22) RVA00297480_SLOT(23)
	RVA00297480_SLOT(24) RVA00297480_SLOT(25) RVA00297480_SLOT(26) RVA00297480_SLOT(27)
#undef RVA00297480_SLOT
	virtual Rva00297480Interface *slot70();
};

// ?rva00297480@@YAPAVRva00297480Interface@@PAVObject@@@Z (obj arrives in EAX)
static Rva00297480Interface *rva00297480(Object *obj)
{
	for (char **u = *reinterpret_cast<char ***>(reinterpret_cast<char *>(obj) + 0x1F0); *u; ++u)
	{
		Rva00297480Interface *found =
			reinterpret_cast<Rva00297480ModuleInterface *>(*u + 0xC)->slot70();
		if (found)
			return found;
	}
	return 0;
}

// ?rva00297480Caller@@YAPAVRva00297480Interface@@PAVObject@@@Z absent-from-retail
// TU-local caller that keeps the static above alive with retail's private EAX convention.
Rva00297480Interface *rva00297480Caller(Object *obj)
{
	return rva00297480(obj);
}
