// ?notifyLookedUp@@YAXPAURva0020AA00Owner@@HH@Z
struct Rva0020AA00Target;
// The thunk at 0x00017A12 reaches the matched ThingTemplate row 0x00144DC0.
class AssetList;
class ThingTemplate
{
public:
	void rva00144DC0(AssetList &assets, void *context);
};

// The per-element call goes through ILT 0x00028560 to 0x00137E80, the matched
// ?findTemplate@BfmeThingFactory@@QAEPBVThingTemplate@@ABVAsciiString@@@Z
// (tools/callees.py 0x20aa00 72): the owner's elements are AsciiStrings.
class AsciiString;
class BfmeThingFactory { public: const ThingTemplate *findTemplate(const AsciiString &name); };
// Retail global 0x012EF1D8 is EA's ThingFactory singleton, defined once in
// Common/Thing/ThingFactory.cpp; this TU keeps its own registry view of it.
class ThingFactory;
extern ThingFactory* TheThingFactory;
struct Rva0020AA00Owner { char m_pad[0x20]; int* m_begin; int* m_end; };
void notifyLookedUp(Rva0020AA00Owner* owner, int a, int b)
{
	for (int* it = owner->m_begin; it != owner->m_end; ++it) {
		Rva0020AA00Target* t = (Rva0020AA00Target *)((BfmeThingFactory *)TheThingFactory)->findTemplate(*(const AsciiString *)it);
		if (t)
			reinterpret_cast<ThingTemplate *>(t)->rva00144DC0(*(AssetList *)a, (void *)b);
	}
}
