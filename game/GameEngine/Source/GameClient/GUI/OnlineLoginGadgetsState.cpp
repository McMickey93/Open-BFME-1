// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc

template <typename T> class StringBase
{
	friend class AsciiString;

public:
	int compareNoCase( const T *text ) const;

private:
	StringBase() : m_data( 0 ) {}
	StringBase( const T *text );
	StringBase( const StringBase<T> &other );
	~StringBase() { releaseBuffer(); }
private:
	void releaseBuffer();

	void *m_data;
};

class AsciiString : private StringBase<char>
{
public:
	AsciiString() : StringBase<char>() {}
	AsciiString( const char *text ) : StringBase<char>( text ) {}
	AsciiString( const AsciiString &other ) : StringBase<char>( other ) {}
	~AsciiString() {}

};

bool GetStringFromRegistry( AsciiString path, AsciiString key, AsciiString &value );

class BfmeAptScreenOnlineLogin
{
public:
	bool _bfme_loginGadgetsState();
};

bool BfmeAptScreenOnlineLogin::_bfme_loginGadgetsState()
{
	AsciiString registeredValue;
	GetStringFromRegistry( "", "Registered", registeredValue );
	return ((const StringBase<char> *)&registeredValue)->compareNoCase( "true" ) == 0;
}
