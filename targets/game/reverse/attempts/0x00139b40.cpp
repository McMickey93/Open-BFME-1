// ?newTemplate@ThingFactory@@QAEPAVThingTemplate@@ABVAsciiString@@@Z
// partial score=0.95 date=2026-10-24
// cl: /DNDEBUG /DWIN32 /MD /EHsc
// Shape 0.981 vs retail 0x00139B40 (352 vs 350 bytes). Everything matches
// except the prologue frame: ours does `sub esp,8` because MSVC gives the
// first DefaultThingTemplate temporary its own slot next to the shared
// new-spill/second-temporary slot, while retail fits all three in one
// 4-byte slot allocated with `push ecx` (every [esp+N] displacement is off
// by +4 and the epilogue does `add esp,0x14` instead of `add esp,0x10`).
// Next lead: find the source/IR shape that makes both AsciiString temps
// share one slot (retail's slot is live only across the ctor call, EH
// state 0); operator-delete visibility and eh_levers all tried, no change.
// ?newTemplate@ThingFactory@@QAEPAVThingTemplate@@ABVAsciiString@@@Z
// BFME retail RVA 0x00139B40, 350 bytes. The ZH newTemplate body with the
// BFME1 retail shape: the "DefaultThingTemplate" existence test goes through
// the ***TESTING predicate (also emitted out of line at 0x00137E20, inlined
// here), the copy runs inside the global override-copy bracket, and
// addTemplate is inlined leaving only the opaque hash lookup (NDEBUG
// compiles DEBUG_CRASH out), the list link and the operator[] insert.
// Retail nextID: UnsignedShort at +0x0c; the template's name is the
// AsciiString at +0x20, the next link at +0x38c and the ID at +0x478.

// String model per inputs/reference/shims/stringinline/StringInline.h (copy
// ctor / dtor as inline forwarders to the out-of-line StringBase<char>
// bodies), plus the public StringBase::set that AsciiString::operator=
// inlines to; retail calls it at 0x00887C90.
template <typename T> struct StringInlineData
{
	int m_refCount;
	int m_length;
	T m_text[1];
};

template <typename T> class StringBase
{
	friend class AsciiString;

public:
	void set( const StringBase<T> &other );

private:
	StringBase() : m_data( 0 ) {}
	StringBase( const T *text );
	StringBase( const StringBase<T> &other );
	~StringBase();
	void releaseBuffer();

	StringInlineData<T> *m_data;
};

template <>
inline StringBase<char>::~StringBase()
{
	releaseBuffer();
}

class AsciiString : private StringBase<char>
{
public:
	AsciiString() : StringBase<char>() {}
	AsciiString( const char *text ) : StringBase<char>( text ) {}
	AsciiString( const AsciiString &other ) : StringBase<char>( other ) {}
	~AsciiString() {}
	AsciiString &operator=( const AsciiString &other ) { set( other ); return *this; }
	const char *str( void ) const { return m_data ? m_data->m_text : ""; }
};

// Retail IAT RVA 0x00F594BC is MSVCR71 strncmp (case-sensitive).
typedef unsigned short UnsignedShort;

extern "C" __declspec(dllimport) int __cdecl strncmp(
	const char *, const char *, unsigned int );

class ThingTemplate
{
public:
	ThingTemplate();
	ThingTemplate &operator=( const ThingTemplate &other );
	void setCopiedFromDefault();

	unsigned char m_prefix[0x20];
	AsciiString m_nameString;                              // +0x20
	unsigned char m_middle[0x38c - 0x24];
	ThingTemplate *m_nextTemplate;                         // +0x38c
	unsigned char m_beforeID[0x478 - 0x390];
	unsigned short m_templateID;                           // +0x478
	unsigned char m_tail[0x4d4 - 0x47a];
};
typedef char VerifyThingTemplateSize[sizeof( ThingTemplate ) == 0x4d4 ? 1 : -1];

// Written by the retail copy paths (0x00139A80 / 0x00139B40) around the
// ThingTemplate copy assignment; defined in ThingFactory_newOverride.cpp.
extern bool TheBfmeOverrideCopyInProgress;

// Read-only view of the factory's string-key table, resolved through the
// ledger pins at ILT 0x0001460a (find) and 0x00027147 (operator[]).
struct Rva001366A0Node
{
	void *next;
	AsciiString key;
	ThingTemplate *value;
};
class Rva00137E80Map
{
public:
	Rva001366A0Node *find( const AsciiString & );
	ThingTemplate *&operator[]( const AsciiString & );
};

// Existing retail lookup owner at 0x00137E80.
class BfmeThingFactory
{
public:
	const ThingTemplate *findTemplate( const AsciiString &name );
};

class ThingFactory
{
public:
	ThingTemplate *newTemplate( const AsciiString &name );

	// addTemplate is inlined in retail; NDEBUG compiles the duplicate-name
	// DEBUG_CRASH out and only the opaque hash lookup call remains.
	void addTemplate( ThingTemplate *tmplate )
	{
		m_templateHashMap.find( tmplate->m_nameString );
		tmplate->m_nextTemplate = m_firstTemplate;
		m_firstTemplate = tmplate;
		m_templateHashMap[tmplate->m_nameString] = tmplate;
	}

	// The predicate retail also emits out of line at 0x00137E20.
	bool exists( const AsciiString &name )
	{
		if ( !strncmp( name.str(), "***TESTING", 10 ) )
			return true;
		return m_templateHashMap.find( name ) != 0;
	}

private:
	unsigned char m_prefix[8];
	ThingTemplate *m_firstTemplate;                        // +0x08
	unsigned short m_nextTemplateID;                       // +0x0c
	unsigned char m_pad0e[2];
	Rva00137E80Map m_templateHashMap;                      // +0x10
};

ThingTemplate *ThingFactory::newTemplate( const AsciiString &name )
{
	ThingTemplate *newTemplate = new ThingTemplate;

	// if the default template is present, get it and copy over any data to
	// the new template
	if ( exists( AsciiString( "DefaultThingTemplate" ) ) )
	{
		const ThingTemplate *defaultT =
			reinterpret_cast<BfmeThingFactory *>( this )->findTemplate(
				AsciiString( "DefaultThingTemplate" ) );

		// copy over static data
		TheBfmeOverrideCopyInProgress = true;
		*newTemplate = *defaultT;
		TheBfmeOverrideCopyInProgress = false;
		newTemplate->setCopiedFromDefault();

	}  // end if

	// give template a unique identifier
	UnsignedShort id = m_nextTemplateID;
	m_nextTemplateID = id + 1;
	newTemplate->m_templateID = id;

	// assign name
	newTemplate->m_nameString = name;

	// add to list
	addTemplate( newTemplate );

	// return the newly created template
	return newTemplate;
}
