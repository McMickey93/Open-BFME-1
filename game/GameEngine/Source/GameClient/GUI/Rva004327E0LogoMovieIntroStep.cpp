// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Open-BFME: logo-movie intro timed-op at 0x004327E0 (387 bytes). Same
// (int, bool) ABI as titleScreenIntroStep (0x0042EDC0) and the other steps
// ClientUpdate004329D0::update posts through ILT 0x00049977. With PlayIntro
// (GlobalData+0xBB6) set it plays NewLineMovie, IntelLogo, THXLogo and
// Opening_Game_Cinematic through Display slot 58, letting the middle two be
// skipped once OptionPreferences records HasSeenLogoMovies, then writes that
// preference. It sets the after-intro flag (+0xBB7) and returns 5, or 7 when
// not starting. The step keeps the address.

#include "ascii_string.h"

#define BFME_VSLOT(n) virtual void slot##n();

class GameEngine
{
public:
	BFME_VSLOT(0) BFME_VSLOT(1) BFME_VSLOT(2) BFME_VSLOT(3) BFME_VSLOT(4)
	BFME_VSLOT(5) BFME_VSLOT(6) BFME_VSLOT(7) BFME_VSLOT(8) BFME_VSLOT(9)
	BFME_VSLOT(10) BFME_VSLOT(11) BFME_VSLOT(12) BFME_VSLOT(13) BFME_VSLOT(14)
	BFME_VSLOT(15)
	virtual void serviceWindowsOS();
};

class Display
{
public:
	BFME_VSLOT(0) BFME_VSLOT(1) BFME_VSLOT(2) BFME_VSLOT(3) BFME_VSLOT(4)
	BFME_VSLOT(5) BFME_VSLOT(6) BFME_VSLOT(7) BFME_VSLOT(8) BFME_VSLOT(9)
	BFME_VSLOT(10) BFME_VSLOT(11) BFME_VSLOT(12) BFME_VSLOT(13) BFME_VSLOT(14)
	BFME_VSLOT(15) BFME_VSLOT(16) BFME_VSLOT(17) BFME_VSLOT(18) BFME_VSLOT(19)
	BFME_VSLOT(20) BFME_VSLOT(21) BFME_VSLOT(22) BFME_VSLOT(23) BFME_VSLOT(24)
	BFME_VSLOT(25) BFME_VSLOT(26) BFME_VSLOT(27) BFME_VSLOT(28) BFME_VSLOT(29)
	BFME_VSLOT(30) BFME_VSLOT(31) BFME_VSLOT(32) BFME_VSLOT(33) BFME_VSLOT(34)
	BFME_VSLOT(35) BFME_VSLOT(36) BFME_VSLOT(37) BFME_VSLOT(38) BFME_VSLOT(39)
	BFME_VSLOT(40) BFME_VSLOT(41) BFME_VSLOT(42) BFME_VSLOT(43) BFME_VSLOT(44)
	BFME_VSLOT(45) BFME_VSLOT(46) BFME_VSLOT(47) BFME_VSLOT(48) BFME_VSLOT(49)
	BFME_VSLOT(50) BFME_VSLOT(51) BFME_VSLOT(52) BFME_VSLOT(53) BFME_VSLOT(54)
	BFME_VSLOT(55) BFME_VSLOT(56) BFME_VSLOT(57)
	// BFME's logo player takes a skip-allowed flag where Zero Hour takes a
	// minimum movie length.
	virtual void playLogoMovie(AsciiString movieName, bool allowSkip, int minCopyrightLength);
};

#undef BFME_VSLOT

class GlobalData
{
public:
	unsigned char m_padB80[0xBB6];
	bool m_playIntro;	///< +0xBB6
	bool m_afterIntro;	///< +0xBB7
};

extern GameEngine *TheGameEngine;
extern Display *TheDisplay;
extern GlobalData *TheWritableGlobalData;

// The preference map is STLport's map<AsciiString, AsciiString>; only its
// out-of-line operator[] (0x0047DF70) is called here.
namespace _STL
{
template <class T> struct less {};
template <class A, class B> struct pair {};
template <class T> class allocator {};
template <class K, class V, class C, class A>
class map
{
public:
	V &operator[](const K &key);

private:
	char m_tree[12];
};
}

typedef _STL::map<AsciiString, AsciiString, _STL::less<AsciiString>,
	_STL::allocator<_STL::pair<const AsciiString, AsciiString> > > PreferenceMap;

// The retail map lookup is reached through this existing ILT. Keep its
// observed member ABI without depending on competing template emitters.
extern void j_0003e6da();


class UserPreferences : public PreferenceMap
{
public:
	virtual ~UserPreferences();
	virtual bool write();

protected:
	AsciiString m_filename;
};

class OptionPreferences : public UserPreferences
{
public:
	OptionPreferences();
	virtual ~OptionPreferences();
	bool hasSeenLogoMovies();
};

// Retail inlines AsciiString::operator=(const char *) as an explicit-length
// StringBase<char>::set.
extern "C" unsigned int __cdecl strlen(const char *);
#pragma intrinsic(strlen)
static inline void assignText(AsciiString &s, const char *text)
{
	static_cast<StringBase<char> &>(s).set(text, strlen(text));
}

// ?Rva004327E0@@YAHH_N@Z
int Rva004327E0(int, bool start)
{
	int result = 5;
	TheGameEngine->serviceWindowsOS();
	if (start)
	{
		if (TheWritableGlobalData->m_playIntro)
		{
			OptionPreferences prefs;
			bool seen = prefs.hasSeenLogoMovies();
			TheDisplay->playLogoMovie("NewLineMovie", false, 8);
			TheDisplay->playLogoMovie("IntelLogo", seen, 8);
			TheDisplay->playLogoMovie("THXLogo", seen, 8);
			TheDisplay->playLogoMovie("Opening_Game_Cinematic", true, 0x30);
            union {
                void (*raw)();
                AsciiString &(PreferenceMap::*lookup)(const AsciiString &);
            } target;
            target.raw = j_0003e6da;
            assignText((static_cast<PreferenceMap &>(prefs).*target.lookup)("HasSeenLogoMovies"), "yes");
			prefs.write();
		}
		TheWritableGlobalData->m_afterIntro = true;
	}
	else
		result = 7;
	return result;
}
