// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
// Retail 0x007710F0, 970 bytes. The matched Rva00774060 forwarder calls
// Rva007710F0Owner::method through ILT 0x0003A8D7 with two stack words.
// The owner identity is unproven; its record layouts below keep the address.
// Reuses canonical strings and the verified AssetList insertion operators.
// The first context byte selects one of two 20-byte cached AssetLists at +0x134.
// The name set deduplicates the nested 0xBC-record walk; it is not the output.
// See identity_evidence/00774060-not-test-kindofmask-multi.md for the caller.

#define _BFME_RETAIL_TREE_INSERT_LAYOUT
#include <set>
#include <vector>
#include <string.h>

#include "ascii_string.h"
template <> inline bool StringBase<char>::isEmpty() const
{
    return m_data == 0 || m_data->length == 0;
}

namespace _STL
{
template <> struct less<AsciiString>
{
    bool operator()(const AsciiString &left, const AsciiString &right) const
    {
        return left.compare(right) < 0;
    }
};
}

void *bfmeGoEMEb(void *);
class GameLODManager;
extern GameLODManager *TheGameLODManager;
class ParticleSystemManager;
extern ParticleSystemManager *TheParticleSystemManager;

struct Rva001408C0Target;
typedef Rva001408C0Target *Rva001408C0Key;
typedef Rva001408C0Key (__cdecl *Rva007710F0FindFn)(const char *);
typedef _STL::set<Rva001408C0Key, _STL::less<Rva001408C0Key>,
    _STL::allocator<Rva001408C0Key> > Rva001408C0Set;

class AssetList
{
public:
    AssetList &operator <<(const AssetList &other)
    {
        m_prototypes.insert(other.m_prototypes.begin(),
            other.m_prototypes.end());
        m_changed = true;
        return *this;
    }

    AssetList &operator <<(const AsciiString &name)
    {
        if (m_prototypes.insert(((Rva007710F0FindFn)bfmeGoEMEb)(name.str())).second)
            m_changed = true;
        return *this;
    }

    AssetList &operator <<(const char *name)
    {
        if (name && m_prototypes.insert(((Rva007710F0FindFn)bfmeGoEMEb)(name)).second)
            m_changed = true;
        return *this;
    }

    bool empty() const { return m_prototypes.empty(); }

private:
    Rva001408C0Set m_prototypes;
    unsigned int m_treeLayoutPad;
    bool m_changed;
};

enum Rva00769DD0Mode { RVA00769DD0_MODE_UNKNOWN=-1, RVA00769DD0_MODE_LOW=0,
 RVA00769DD0_MODE_MEDIUM=1, RVA00769DD0_MODE_HIGH=2, RVA00769DD0_MODE_CUSTOM=3, RVA00769DD0_MODE_COUNT=6 };
class Rva00769DD0ModelConditionInfo {
public:
 void preloadAssets(AssetList *, void *, Rva00769DD0Mode, bool);
};

class Rva00769490Owner
{
public:
    void invoke(AssetList *, void *, const AsciiString &, int);
};

class BfmeThing935E
{
public:
    void bfmeGo935E(void *, void *);
};

// insert_unique calls the existing 183-byte retail _M_insert at 0x000BFCC0
// through ILT 0x00032B87. Leave its native specialization to that provider;
// instantiating it here creates a different copy under the same identity.
typedef _STL::_Rb_tree<AsciiString, AsciiString, _STL::_Identity<AsciiString>,
    _STL::less<AsciiString>, _STL::allocator<AsciiString> > Rva007710F0NameTree;
namespace _STL {
template <> Rva007710F0NameTree::iterator Rva007710F0NameTree::_M_insert(
    _Rb_tree_node_base *, _Rb_tree_node_base *, const AsciiString &, _Rb_tree_node_base *);
}

typedef _STL::set<AsciiString> Rva007710F0NameSet;

struct Rva007710F0Outer
{
    unsigned char m_pad0[0x34];
    AsciiString m_key;
    unsigned char m_pad38[0xf0];
};

struct Rva007710F0Nested
{
    unsigned char m_body[0xbc];
};

struct Rva007710F0InnerName
{
    AsciiString m_name;
    unsigned char m_pad04[4];
};

struct Rva007710F0Record6C
{
    unsigned char m_pad0[0x10];
    Rva007710F0InnerName *m_begin;
    Rva007710F0InnerName *m_end;
    unsigned char m_pad18[0x54];
};

struct Rva007710F0Elem14
{
    unsigned int m_unknown00;
    _STL::vector<AsciiString> m_names;
    unsigned int m_unknown10;
};

struct Rva007710F0Elem2C
{
    const char *m_name;
    unsigned char m_pad04[0x28];
};

struct Rva007710F0Lod
{
    unsigned char m_pad0[0x16c4];
    int m_level;
};

class Rva007710F0Owner
{
public:
    void method(void *first, void *context);

private:
    unsigned char m_pad0[8];
    _STL::vector<Rva007710F0Record6C> m_records08;
    AsciiString m_name14;
    _STL::vector<Rva007710F0Outer> m_outer18;
    _STL::vector<Rva007710F0Nested> m_nested24;
    unsigned char m_pad30[0xc];
    AsciiString m_name3c;
    unsigned char m_pad40[0x2c];
    _STL::vector<Rva007710F0Elem2C> m_names6c;
    _STL::vector<Rva007710F0Elem14> m_names78;
    const char *m_final84;
    unsigned char m_pad88[0x83];
    bool m_flag10b;
    unsigned char m_pad10c[0x28];
    AssetList m_assetLists[2];
};

void Rva007710F0Owner::method(void *first, void *context)
{
    AssetList *assets = (AssetList *)first;
    unsigned char which = *(unsigned char *)context;
    unsigned int index = which != 0;
    // Keep the indexed receiver view until each insertion takes its list
    // address. Retail forms this + index*20 before adding the +0x134 member.
    Rva007710F0Owner *variant = (Rva007710F0Owner *)((char *)this + index * sizeof(AssetList));

    if (!variant->m_assetLists[0].empty())
    {
        *assets << variant->m_assetLists[0];
        return;
    }

    Rva00769DD0Mode level = (Rva00769DD0Mode)reinterpret_cast<Rva007710F0Lod *>(TheGameLODManager)->m_level;
    if (which)
        level = RVA00769DD0_MODE_MEDIUM;

    for (Rva007710F0Record6C *record = m_records08.begin();
        record != m_records08.end(); ++record)
    {
        for (Rva007710F0InnerName *name = record->m_begin;
            name != record->m_end; ++name)
            variant->m_assetLists[0] << name->m_name;
    }

    if (!m_name14.isEmpty())
    {
        reinterpret_cast<BfmeThing935E *>(TheParticleSystemManager)->bfmeGo935E(&m_name14, &variant->m_assetLists[0]);
    }

    if (!m_name3c.isEmpty())
        variant->m_assetLists[0] << (m_name3c + ".tga");

    Rva007710F0NameSet names;
    for (Rva007710F0Outer *outer = m_outer18.begin();
        outer != m_outer18.end(); ++outer)
    {
        ((Rva00769DD0ModelConditionInfo *)outer)->preloadAssets(&variant->m_assetLists[0], context,
            level, m_flag10b);
        if (names.find(outer->m_key) == names.end())
        {
            names.insert(outer->m_key);
            for (Rva007710F0Nested *nested = m_nested24.begin();
                nested != m_nested24.end(); ++nested)
                ((Rva00769490Owner *)nested)->invoke(&variant->m_assetLists[0], context, outer->m_key, level);
        }
    }

    for (Rva007710F0Elem14 *item = m_names78.begin();
        item != m_names78.end(); ++item)
    {
        for (AsciiString *name = item->m_names.begin(); name != item->m_names.end(); ++name)
            variant->m_assetLists[0] << *name;
    }

    for (Rva007710F0Elem2C *item = m_names6c.begin();
        item != m_names6c.end(); ++item)
        variant->m_assetLists[0] << item->m_name;

    variant->m_assetLists[0] << m_final84;

    *assets << variant->m_assetLists[0];
}
