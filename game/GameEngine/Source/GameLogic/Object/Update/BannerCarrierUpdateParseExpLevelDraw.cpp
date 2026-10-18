// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib /Iinputs/reference/shims/iniexception
// stlport
// BannerCarrierUpdateModuleData::parseExpLevelDraw, the "ExpLevelDraw"
// FieldParse callback (field row VA 0x010BBD88, store offset 0x24, called
// through ILT 0x00049D50). ilt_oracle CONFIRMS (exact) that decoration and the
// ExpLevelDraw element type of the store vector (push_back at ILT
// 0x0004B2C2). The sub-object element type is unproven: its vector's
// _M_insert_overflow is the pointer-vector body at 0x00284100.

#include <string.h>
#include "ascii_string.h"
// Retail expands set(const char *) here: inline strlen, then set(text, length).
template<> inline void StringBase<char>::set( const char *s ) { set( s, s ? strlen( s ) : 0 ); }
#include "Common/INIException.h"
#include <vector>

class INI
{
public:
	const char *getNextToken( const char *seps );
	const char *getNextTokenOrNull( const char *seps );
	const char *getSepsColon( void ) const { return m_sepsColon; }
	static int scanInt( const char *token );

	char m_unreconstructed_000[ 0x41c ];
	const char *m_sepsColon;
};

// One "SubObject Show|Hide <name>" entry.
struct Rva00284E70SubObject
{
	AsciiString m_name;
	bool m_show;
};

class BannerCarrierUpdateModuleData
{
public:
	// One "Level <n> SubObject ..." line.
	struct ExpLevelDraw
	{
		int m_level;
		_STL::vector<Rva00284E70SubObject *> m_subObjects;
	};

	static void parseExpLevelDraw( INI *ini, void *instance, void *store, const void *userData );
};

void BannerCarrierUpdateModuleData::parseExpLevelDraw( INI *ini, void *instance, void *store, const void *userData )
{
	ExpLevelDraw *level = new ExpLevelDraw;

	const char *token = ini->getNextTokenOrNull( ini->getSepsColon() );
	if ( token == 0 || strcmp( token, "Level" ) != 0 )
		throw INIException( 3, "UnitType expected" );
	level->m_level = INI::scanInt( ini->getNextToken( ini->getSepsColon() ) );

	token = ini->getNextTokenOrNull( ini->getSepsColon() );
	while ( token != 0 )
	{
		if ( token == 0 || strcmp( token, "SubObject" ) != 0 )
			throw INIException( 3, "'ModelState' expected" );
		Rva00284E70SubObject *subObject = new Rva00284E70SubObject;
		const char *visibility = ini->getNextToken( ini->getSepsColon() );
		subObject->m_show = _strcmpi( visibility, "Show" ) == 0;
		subObject->m_name.set( ini->getNextToken( ini->getSepsColon() ) );
		level->m_subObjects.push_back( subObject );
		token = ini->getNextTokenOrNull( ini->getSepsColon() );
	}
	( (_STL::vector<ExpLevelDraw *> *)store )->push_back( level );
}
