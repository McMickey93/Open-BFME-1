// cl: /DNDEBUG /MD /EHsc
//
// BannerUI.apt helpers. DeleteBanner is reloc-named by the matched
// BannerUI::removeMovieBanner caller; AddBanner / SetBannerProgress share the
// same sprintf / BannerUI.apt lookup / scripted-UI dispatch shape.
// SetBannerState homes the movie temporary in the dead state arg slot
// (retail sub esp,0x10) — a named local adds 4B.

extern "C" __declspec(dllimport) int __cdecl sprintf(
	char *destination, const char *format, ... );

template <typename T> class StringBase
{
	friend class AsciiString;

private:
	StringBase( const T *text );
	StringBase( const StringBase<T> &other );
	~StringBase() { releaseBuffer(); }
private:
	void releaseBuffer();

	void *m_data;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/AsciiString.h
class AsciiString : private StringBase<char>
{
public:
	AsciiString( const char *text ) : StringBase<char>( text ) {}
	AsciiString( const AsciiString &other ) : StringBase<char>( other ) {}
	~AsciiString() {}
	const char *str() const { return m_data ? (const char *)m_data + 8 : ""; }
};

class WindowManager
{
public:
	int findAptMovieIndex( const AsciiString &movie );

};

// ILT 0x00015235 forwards to the matched eight-word body at 0x004675F0.
// Reuse its established owner and ABI, as the other APT dispatch callers do.
class BfmeLevelAN
{
public:
	char *bfmeBuildAN(unsigned int, int, int, int, int, int, int, int);
};

extern WindowManager *g_rva012F19E8WindowManager;

void DeleteBanner( int id )
{
	char idText[ 16 ];
	sprintf( idText, "%d", id );
	AsciiString movie( "BannerUI.apt" );
	((BfmeLevelAN *)g_rva012F19E8WindowManager)->bfmeBuildAN(
		g_rva012F19E8WindowManager->findAptMovieIndex( movie ),
		(int)"DeleteBanner", 1, (int)idText, 0, 0, 0, 0 );
}

void AddBanner( int id, const AsciiString &name, const AsciiString &label )
{
	char idText[ 16 ];
	sprintf( idText, "%d", id );
	AsciiString movie( "BannerUI.apt" );
	((BfmeLevelAN *)g_rva012F19E8WindowManager)->bfmeBuildAN(
		g_rva012F19E8WindowManager->findAptMovieIndex( movie ),
		(int)"AddBanner", 3, (int)idText, (int)name.str(), (int)label.str(), 0, 0 );
}

void SetBannerState( int id, unsigned int state )
{
	char idText[ 16 ];
	const char *label;
	sprintf( idText, "%d", id );
	switch( state )
	{
	case 0: label = "_available"; break;
	case 1: label = "_engaging"; break;
	case 2: label = "_waiting"; break;
	case 3: label = "_disabled"; break;
	default: return;
	}
	((BfmeLevelAN *)g_rva012F19E8WindowManager)->bfmeBuildAN(
		g_rva012F19E8WindowManager->findAptMovieIndex( AsciiString( "BannerUI.apt" ) ),
		(int)"SetBannerState", 2, (int)idText, (int)label, 0, 0, 0 );
}

void SetBannerProgress( int id, int progress )
{
	char idText[ 16 ];
	char progressText[ 16 ];
	sprintf( idText, "%d", id );
	sprintf( progressText, "%d", progress );
	AsciiString movie( "BannerUI.apt" );
	((BfmeLevelAN *)g_rva012F19E8WindowManager)->bfmeBuildAN(
		g_rva012F19E8WindowManager->findAptMovieIndex( movie ),
		(int)"SetBannerProgress", 2, (int)idText, (int)progressText, 0, 0, 0 );
}
