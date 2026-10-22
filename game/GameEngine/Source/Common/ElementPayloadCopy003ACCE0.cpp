// A second emission of the sixteen-byte payload copy walk.
//
// The retail image carries the same fifty-seven bytes twice, at 0x003A8340 and
// at 0x003ACCE0, both reaching the same first-store global. The first was
// converted in ElementPayloadConstructors.cpp; this is the other, instantiated
// over its own element type so the two rows stay distinct.

// Retail's 0x010EC760 vtable is the table ParseFlashRegionsEvent.cpp emits for
// Rva003B7190Record (the same one Rva003A6360CopyCtor.cpp installs).
extern "C" const void *__identifier("??_7Rva003B7190Record@@6B@")[];

struct Gen_t_003acce0_p16cd
{
	void * m_at00;
	int m_at04;
	char m_at08;
	char m_pad09[ 3 ];
	int m_at0C;
};

namespace _STL
{
struct __false_type {};

template <class Input, class Output>
Output __uninitialized_copy( Input first, Input last, Output result, const __false_type & )
{
	for ( ; first != last; ++first, ++result )
	{
		if ( result != 0 )
		{
			result->m_at00 = (void *)__identifier("??_7Rva003B7190Record@@6B@");
			result->m_at04 = first->m_at04;
			result->m_at08 = first->m_at08;
			result->m_at0C = first->m_at0C;
		}
	}
	return result;
}
}

template Gen_t_003acce0_p16cd * _STL::__uninitialized_copy<const Gen_t_003acce0_p16cd *, Gen_t_003acce0_p16cd *>(
	const Gen_t_003acce0_p16cd *, const Gen_t_003acce0_p16cd *, Gen_t_003acce0_p16cd *, const _STL::__false_type & );
