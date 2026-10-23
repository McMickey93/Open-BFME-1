// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Open-BFME5: preserve retail's out-of-line pinputs/reference/string call boundaries.

class AsciiString;

#include "string_base.h"

#include "ascii_string.h"

namespace _STL
{
template <typename T> struct less;
template <typename T> class allocator;
template <typename First, typename Second> struct pair;

template <typename Key, typename Value, typename Compare,
          typename Allocator>
class map
{
public:
    Value &operator[](const Key &key);
};
}

typedef _STL::map<AsciiString, AsciiString, _STL::less<AsciiString>,
                  _STL::allocator<_STL::pair<const AsciiString, AsciiString> > >
    PreferenceMap;

// The retail map lookup is reached through this existing ILT. Keep its
// observed member ABI without depending on competing template emitters.
extern void j_0003e6da();


// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/UserPreferences.h
class UserPreferences : public PreferenceMap
{
public:
    virtual ~UserPreferences();
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/UserPreferences.h
class OptionPreferences : public UserPreferences
{
public:
    virtual ~OptionPreferences();
    void setCampaignDifficulty(int value);
};

void OptionPreferences::setCampaignDifficulty(int value)
{
    AsciiString text;
    text.format("%d", value);
    union {
        void (*raw)();
        AsciiString &(PreferenceMap::*lookup)(const AsciiString &);
    } target;
    target.raw = j_0003e6da;
    (reinterpret_cast<PreferenceMap *>(reinterpret_cast<char *>(this) + 4)->*target.lookup)("CampaignDifficulty") = text;
}
