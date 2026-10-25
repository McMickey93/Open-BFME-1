// cl: /DNDEBUG /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/Wwutil /Igame/Libraries/Source/WWVegas/WWDownload /Igame/Libraries/Source/Compression /Igame/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/shims/sweep

#include "systimer.h"

// Share Get's native initialization flag without emitting its wrong local copy.
extern bool __identifier("?is_init@?1??Get@SysTimeClass@@QAEKXZ@4_NA");

SysTimeClass SystemTime;


SysTimeClass::SysTimeClass(void) :
	StartTime(0),
	WrapAdd(0)
{
	//tell windows we need single ms precision.
	timeBeginPeriod(1);
}

SysTimeClass::~SysTimeClass(void)
{
	//tell windows we need single ms precision.
	timeEndPeriod(1);
}

void SysTimeClass::Reset(void)
{
	StartTime = timeGetTime();
	WrapAdd = 0 - StartTime;
}


bool SysTimeClass::Is_Getting_Late(void)
{
	/*
	** Even though the timers are all unsigned so we have a max time of 0xffffffff the game casts it to int in various places
	** so it's safer to assume a signed max value.
	*/
	if (!__identifier("?is_init@?1??Get@SysTimeClass@@QAEKXZ@4_NA")) {
		Reset();
		__identifier("?is_init@?1??Get@SysTimeClass@@QAEKXZ@4_NA") = true;
	}
	unsigned long now = timeGetTime();
	unsigned long elapsed;
	if (now > StartTime) elapsed = now - StartTime;
	else elapsed = now + WrapAdd;
	if (elapsed > 0x6fffffff) {
		return(true);
	}
	return(false);
}


