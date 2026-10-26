// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/ini /Iinputs/reference/shims/iniexception /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main
// stlport

// FILE: CloudEffect.cpp //////////////////////////////////////////////////////
//
// The CloudEffect block, BFME-only, next door to CloudBreakEffect and the same
// shape: copy saved into active, parse over active, write back unless this is an
// override load, then poke the cloud system through vtable slot 9.
//
// CloudBreakEffect.cpp records this one as unclaimable because its settings
// struct copies through a compiler-generated operator= that nothing in the image
// names. That is true, and it is also the way in: the generated body at
// 0x0040B430 is 295 bytes of member copies and it spells the whole layout out.
// Reconstructing the struct from it makes MSVC generate the same operator=, and
// the pin then names our own symbol rather than a retail one.
//
// Layout read straight off 0x0040B430: five AsciiStrings (0x00, 0x04, 0x08,
// 0x14, 0x88), four twelve-byte PODs copied by lea plus three dword moves
// (0x20, 0x44, 0x54, 0x64), three bytes at 0x3C-0x3E, and plain dwords for the
// rest. Only the shapes are recoverable, not the meanings, so the members are
// named for their offsets.
//
///////////////////////////////////////////////////////////////////////////////
#include "PreRTS.h"
#include "Common/INI.h"

static INILoadType retailLoadType( const INI *ini )
{
	struct RetailINI { char m_pad[ 0x08 ]; INILoadType m_loadType; };
	return reinterpret_cast<const RetailINI *>( ini )->m_loadType;
}

static const INILoadType INI_LOAD_BFME_TYPE_4 = (INILoadType)4;

// Twelve bytes copied as three dwords through a lea - a nested POD, not three
// loose members.
struct CloudEffectTriple
{
	Real m_x;
	Real m_y;
	Real m_z;
};

struct CloudEffect
{
	AsciiString m_string00;
	AsciiString m_string04;
	AsciiString m_string08;
	Int m_int0C;
	Int m_int10;
	AsciiString m_string14;
	Int m_int18;
	Int m_int1C;
	CloudEffectTriple m_triple20;
	Int m_int2C;
	Int m_int30;
	Int m_int34;
	Int m_int38;
	Bool m_bool3C;
	Bool m_bool3D;
	Bool m_bool3E;
	Int m_int40;
	CloudEffectTriple m_triple44;
	Int m_int50;
	CloudEffectTriple m_triple54;
	Int m_int60;
	CloudEffectTriple m_triple64;
	Int m_int70;
	Int m_int74;
	Int m_int78;
	Int m_int7C;
	Int m_int80;
	Int m_int84;
	AsciiString m_string88;

	static const FieldParse m_fieldParseTable[];
};

// Complete retail FieldParse table at VA010F0690, including its zero terminator.
extern const char g_Va010F0ACC[] = "CloudTexture";
extern const char g_Va010F0AB8[] = "DarkCloudTexture";
extern const char g_Va010F0AA8[] = "AlphaTexture";
extern const char g_Va010F0A94[] = "PropagateSpeed";
extern const char g_Va01075378[] = "Angle";
extern const char g_Va010F0A80[] = "DissipateTexture";
extern const char g_Va010F0A68[] = "DissipateStartLevel";
extern const char g_Va010F0A54[] = "DissipateSpeed";
extern const char g_Va010F0A40[] = "DarkeningFactor";
extern const char g_Va010F0A30[] = "DarkeningRate";
extern const char g_Va010F0A1C[] = "LighteningRate";
extern const char g_Va010F0A08[] = "CloudScrollSpeed";
extern const char g_Va010F09F0[] = "DissipateRateScale";
extern const char g_Va010F09DC[] = "LightningShadows";
extern const char g_Va010F09B8[] = "JitterLightningLightPosition";
extern const char g_Va010F0994[] = "JitterLightningLightIntensity";
extern const char g_Va010F0980[] = "LightningChance";
extern const char g_Va010F0964[] = "LightningShadowColor";
extern const char g_Va010F0944[] = "LightningShadowIntensity";
extern const char g_Va010F092C[] = "LightningDuration";
extern const char g_Va010F0914[] = "LightningFrequency";
extern const char g_Va010F08FC[] = "LightningIntensity";
extern const char g_Va010F08E0[] = "LightningLightPosition1";
extern const char g_Va010F08C4[] = "LightningLightPosition2";
extern const char g_Va010F08A8[] = "LightningLightPosition3";
extern const char g_Va010F0898[] = "LightningFX";

const FieldParse CloudEffect::m_fieldParseTable[] =
{
	{ g_Va010F0ACC, INI::parseAsciiString, 0, 0x00 },
	{ g_Va010F0AB8, INI::parseAsciiString, 0, 0x04 },
	{ g_Va010F0AA8, INI::parseAsciiString, 0, 0x08 },
	{ g_Va010F0A94, INI::parseReal, 0, 0x0C },
	{ g_Va01075378, INI::parseInt, 0, 0x10 },
	{ g_Va010F0A80, INI::parseAsciiString, 0, 0x14 },
	{ g_Va010F0A68, INI::parseReal, 0, 0x18 },
	{ g_Va010F0A54, INI::parseReal, 0, 0x1C },
	{ g_Va010F0A40, INI::parseRGBColor, 0, 0x20 },
	{ g_Va010F0A30, INI::parseInt, 0, 0x2C },
	{ g_Va010F0A1C, INI::parseInt, 0, 0x30 },
	{ g_Va010F0A08, INI::parseReal, 0, 0x34 },
	{ g_Va010F09F0, INI::parseReal, 0, 0x38 },
	{ g_Va010F09DC, INI::parseBool, 0, 0x3C },
	{ g_Va010F09B8, INI::parseBool, 0, 0x3D },
	{ g_Va010F0994, INI::parseBool, 0, 0x3E },
	{ g_Va010F0980, INI::parseReal, 0, 0x40 },
	{ g_Va010F0964, INI::parseRGBColor, 0, 0x44 },
	{ g_Va010F0944, INI::parseReal, 0, 0x50 },
	{ g_Va010F092C, INI::parseGameClientRandomVariable, 0, 0x54 },
	{ g_Va010F0914, INI::parseReal, 0, 0x60 },
	{ g_Va010F08FC, INI::parseGameClientRandomVariable, 0, 0x64 },
	{ g_Va010F08E0, INI::parseCoord2D, 0, 0x70 },
	{ g_Va010F08C4, INI::parseCoord2D, 0, 0x78 },
	{ g_Va010F08A8, INI::parseCoord2D, 0, 0x80 },
	{ g_Va010F0898, INI::parseAsciiString, 0, 0x88 },
	{ 0, 0, 0, 0 }
};

class CloudEffectSystem
{
public:
	virtual void _bfme_pad_0() = 0;
	virtual void _bfme_pad_1() = 0;
	virtual void _bfme_pad_2() = 0;
	virtual void _bfme_pad_3() = 0;
	virtual void _bfme_pad_4() = 0;
	virtual void _bfme_pad_5() = 0;
	virtual void _bfme_pad_6() = 0;
	virtual void _bfme_pad_7() = 0;
	virtual void _bfme_pad_8() = 0;
	virtual void settingsChanged() = 0;		// slot 9, +0x24
};

extern CloudEffect TheCloudEffectSaved;			// 0x012F1108
// 0x012F1198 is the destination global Rva0040B7D0Assign.cpp defines as
// g_rva0040b7d0_dst (dir32_addresses.csv); spelling it TheCloudEffectActive
// claimed a second name on an address nothing defines.
extern CloudEffect g_rva0040b7d0_dst;			// 0x012F1198
// A different pointer from the one CloudBreakEffect.cpp reaches at 0x012F10F0:
// this block pokes 0x012F1104. Spelled apart rather than sharing that name,
// which would claim one global at two addresses.
extern CloudEffectSystem *TheCloudEffectSystem;	// 0x012F1104

// ?parseCloudEffect@@YAXPAVINI@@@Z
void parseCloudEffect( INI *ini )
{
	g_rva0040b7d0_dst = TheCloudEffectSaved;
	ini->initFromINI( &g_rva0040b7d0_dst, CloudEffect::m_fieldParseTable );

	const INILoadType loadType = retailLoadType( ini );
	if( loadType != INI_LOAD_CREATE_OVERRIDES && loadType != INI_LOAD_BFME_TYPE_4 )
		TheCloudEffectSaved = g_rva0040b7d0_dst;

	if( TheCloudEffectSystem )
		TheCloudEffectSystem->settingsChanged();
}
