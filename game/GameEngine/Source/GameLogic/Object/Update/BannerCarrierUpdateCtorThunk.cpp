// cl: /DNDEBUG /MD /EHsc

// 0x00285F10, the body this ILT reaches, is BattlePlanUpdateModuleData's constructor,
// written in BattlePlanUpdateModuleDataConstructor.cpp (it was a naked byte lift
// misnamed ??0BannerCarrierUpdate here).

class Rva000287C7FactoryCtorTarget
{
public:
	void construct();
};

class Rva000287C7FactoryCtorThunk
{
public:
	void operator()();
};

void Rva000287C7FactoryCtorThunk::operator()()
{
	((Rva000287C7FactoryCtorTarget *)this)->construct();
}
