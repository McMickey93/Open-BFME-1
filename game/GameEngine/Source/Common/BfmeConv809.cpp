class BfmeSubEFJ
{
	unsigned char m_bfmeHead[4];
};

// The thunk at 0x00017A12 reaches the matched ThingTemplate row 0x00144DC0.
class AssetList;
class ThingTemplate
{
public:
	void rva00144DC0(AssetList &assets, void *context);
};

class AsciiString;
class BfmeThingFactory
{
public:
    const ThingTemplate *findTemplate(const AsciiString &name);
};

// Retail global 0x012EF1D8 is EA's ThingFactory singleton, defined once in
// Common/Thing/ThingFactory.cpp. Use the rowed factory lookup contract.
class ThingFactory;

extern ThingFactory *TheThingFactory;

struct BfmeThingEFJa
{
	void bfmeGoEFJa(void *a, void *b);
	unsigned char m_bfmeHead[0x5c];
	BfmeSubEFJ m_bfmeSub;
};

void BfmeThingEFJa::bfmeGoEFJa(void *a, void *b)
{
	const ThingTemplate *r = reinterpret_cast<BfmeThingFactory *>(TheThingFactory)->findTemplate(
        *reinterpret_cast<const AsciiString *>(&m_bfmeSub));
	if (r)
		const_cast<ThingTemplate *>(r)->rva00144DC0(*static_cast<AssetList *>(a), b);
}

struct BfmeThingEFJb
{
	void bfmeGoEFJb(void *a, void *b);
	unsigned char m_bfmeHead[0xb4];
	BfmeSubEFJ m_bfmeSub;
};

void BfmeThingEFJb::bfmeGoEFJb(void *a, void *b)
{
	const ThingTemplate *r = reinterpret_cast<BfmeThingFactory *>(TheThingFactory)->findTemplate(
        *reinterpret_cast<const AsciiString *>(&m_bfmeSub));
	if (r)
		const_cast<ThingTemplate *>(r)->rva00144DC0(*static_cast<AssetList *>(a), b);
}
