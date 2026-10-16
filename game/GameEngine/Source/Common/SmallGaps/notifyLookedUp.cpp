// ?notifyLookedUp@@YAXPAURva0020AA00Owner@@HH@Z
struct Rva0020AA00Target;
// The thunk at 0x00017A12 reaches the matched ThingTemplate row 0x00144DC0.
class AssetList;
class ThingTemplate
{
public:
	void rva00144DC0(AssetList &assets, void *context);
};

struct Rva0020AA00Registry { Rva0020AA00Target* lookup(const int& id); };
// Retail global 0x012EF1D8 is EA's ThingFactory singleton, defined once in
// Common/Thing/ThingFactory.cpp; this TU keeps its own registry view of it.
class ThingFactory;
extern ThingFactory* TheThingFactory;
struct Rva0020AA00Owner { char m_pad[0x20]; int* m_begin; int* m_end; };
void notifyLookedUp(Rva0020AA00Owner* owner, int a, int b)
{
	for (int* it = owner->m_begin; it != owner->m_end; ++it) {
		Rva0020AA00Target* t = ((Rva0020AA00Registry *)TheThingFactory)->lookup(*it);
		if (t)
			reinterpret_cast<ThingTemplate *>(t)->rva00144DC0(*(AssetList *)a, (void *)b);
	}
}
