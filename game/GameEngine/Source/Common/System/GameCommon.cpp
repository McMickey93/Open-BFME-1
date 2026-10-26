// cl: /DNDEBUG /MD /EHsc /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug
// stlport
#include "PreRTS.h"
#include "Common/GameCommon.h"

// GameCommon.cpp owns this enum table upstream. Retail VA 0x012A9FB4
// has the same four names and null terminator; each keyword owns its
// independently verified retail storage rather than a compiler literal pin.
extern const char g_Va01087B00[] = "REGULAR";
extern const char g_Va01073AA0[] = "VETERAN";
extern const char g_Va01073A98[] = "ELITE";
extern const char g_Va01087AF8[] = "HEROIC";

const char *TheVeterancyNames[] =
{
	g_Va01087B00,
	g_Va01073AA0,
	g_Va01073A98,
	g_Va01087AF8,
	NULL
};

//-------------------------------------------------------------------------------------------------
Real normalizeAngle(Real angle)
{
	while (angle > PI)
		angle -= 2*PI;

	while (angle <= -PI)
		angle += 2*PI;

	return angle;
}
