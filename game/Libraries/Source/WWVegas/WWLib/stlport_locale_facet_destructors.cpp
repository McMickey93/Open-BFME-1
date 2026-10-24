// cl: /O2 /EHsc /MD /D_STLP_USE_STATIC_LIB
// STLport 4.5.3

typedef unsigned short wchar_t;

namespace _STL
{

// STLport 4.5.3 _threads.h, single-threaded: the count alone.
class _Refcount_Base
{
public:
	_Refcount_Base( size_t __n ) : _M_ref_count( __n ) {}

	size_t _M_ref_count;
};

class locale
{
public:
	// STLport 4.5.3 _locale.h: the delete-on-last-release flag follows the
	// _Refcount_Base count.
	class facet : protected _Refcount_Base
	{
	protected:
		explicit facet( size_t __no_del = 0 ) : _Refcount_Base( 1 ), _M_delete( __no_del == 0 ) {}
		virtual ~facet();

	private:
		bool _M_delete;
	};
};

template <class CharT>
class ctype : public locale::facet
{
public:
	explicit ctype( size_t __refs = 0 ) : locale::facet( __refs ) {}

protected:
	virtual ~ctype();
};

template <class CharT>
ctype<CharT>::~ctype()
{
}

template class ctype<wchar_t>;

template <class InternT, class ExternT, class StateT>
class codecvt : public locale::facet
{
public:
	explicit codecvt( size_t __refs = 0 ) : locale::facet( __refs ) {}

protected:
	virtual ~codecvt();
};

template <class InternT, class ExternT, class StateT>
codecvt<InternT, ExternT, StateT>::~codecvt()
{
}

template class codecvt<char, char, int>;
template class codecvt<wchar_t, char, int>;

template <class CharT>
class collate : public locale::facet
{
public:
	explicit collate( size_t __refs = 0 ) : locale::facet( __refs ) {}

protected:
	virtual ~collate();
};

template <class CharT>
collate<CharT>::~collate()
{
}

template class collate<char>;
template class collate<wchar_t>;

template <class CharT>
class numpunct : public locale::facet
{
public:
	explicit numpunct( size_t __refs = 0 ) : locale::facet( __refs ) {}

protected:
	virtual ~numpunct();
};

template <class CharT>
numpunct<CharT>::~numpunct()
{
}

template class numpunct<char>;
template class numpunct<wchar_t>;

} // namespace _STL
