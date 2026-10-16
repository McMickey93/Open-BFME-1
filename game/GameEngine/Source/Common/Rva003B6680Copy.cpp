// ??0Rva003B6680@@QAE@ABV0@@Z
// Retail 0x003ABC80 (490 bytes): the copy constructor of the Rva003B6680
// object whose converting constructor and assignment operator are already
// landed (Rva003B6680Ctor.cpp at 0x003B2900, Rva003B6680Assign.cpp at
// 0x003B6680).  It member-copies the string at +4, the twelve 12-byte members,
// the second string at +0x50, the vector at +0xA8 (through
// initialize_base/copyVectorElements), the three trailing members and the flag
// at +0xD8.
//
// Identity stays address-derived, like the rest of the family.
// cl: /O2 /EHsc /MD /DNDEBUG /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS /Igame/Libraries/Source/WWVegas/WWLib
// stlport

#pragma inline_depth(255)
#pragma inline_recursion(on)
#pragma auto_inline(on)


template <typename T>
class Rva003B6680StringBase
{
friend class Rva003B6680AsciiString;

private:
	Rva003B6680StringBase()
	{
	}
	Rva003B6680StringBase(const Rva003B6680StringBase &other);
	void *m_data;
};

class Rva003B6680AsciiString : private Rva003B6680StringBase<char>
{
public:
	__forceinline Rva003B6680AsciiString(const Rva003B6680AsciiString &other)
	{
		((Rva003B6680StringBase<char> *)this)->Rva003B6680StringBase<char>::Rva003B6680StringBase(
			*(const Rva003B6680StringBase<char> *)&other);
	}
	~Rva003B6680AsciiString();
};

#define DECLARE_MEMBER(name, count) \
struct name \
{ \
	int m_data[count]; \
	name(const name &other); \
	~name(); \
}

DECLARE_MEMBER(Rva003B6680Member08, 3);
DECLARE_MEMBER(Rva003B6680Member14, 3);
DECLARE_MEMBER(Rva003B6680Member20, 3);
DECLARE_MEMBER(Rva003B6680Member2C, 3);
DECLARE_MEMBER(Rva003B6680Member38, 3);
DECLARE_MEMBER(Rva003B6680Member44, 3);
DECLARE_MEMBER(Rva003B6680Member54, 3);
DECLARE_MEMBER(Rva003B6680Member60, 3);
DECLARE_MEMBER(Rva003B6680Member6C, 3);
DECLARE_MEMBER(Rva003B6680Member78, 3);
DECLARE_MEMBER(Rva003B6680Member84, 3);
DECLARE_MEMBER(Rva003B6680Member90, 3);
DECLARE_MEMBER(Rva003B6680Member9C, 3);
DECLARE_MEMBER(Rva003B6680MemberB4, 3);
DECLARE_MEMBER(Rva003B6680MemberC0, 3);
DECLARE_MEMBER(Rva003B6680MemberCC, 3);

struct Gen_t_003b4b60_p16cd
{
	virtual void slot0();
	int m_data04;
	char m_data08;
	int m_data0c;
	Gen_t_003b4b60_p16cd(const Gen_t_003b4b60_p16cd &other);
	~Gen_t_003b4b60_p16cd();
};

struct Rva003B6680VectorAllocator
{
	int m_value;
};

struct Rva003B6680FalseType;
Gen_t_003b4b60_p16cd *copyVectorElements(
	const Gen_t_003b4b60_p16cd *first,
	const Gen_t_003b4b60_p16cd *last,
	Gen_t_003b4b60_p16cd *result,
	const Rva003B6680FalseType &tag);

struct Rva003B6680VectorBase
{
	Gen_t_003b4b60_p16cd *m_start;
	Gen_t_003b4b60_p16cd *m_finish;
	Gen_t_003b4b60_p16cd *m_end_of_storage;
	Rva003B6680VectorAllocator get_allocator() const throw();
	void initialize_base(unsigned count, const Rva003B6680VectorAllocator &allocator);
};

struct Rva003B6680Vector : public Rva003B6680VectorBase
{
	__forceinline Rva003B6680Vector(int)
	{
	}

	~Rva003B6680Vector();
	__forceinline void initialize_from(const Rva003B6680VectorBase &source);
};

struct Rva003B6680FalseType
{
    Rva003B6680FalseType() {}
};

__forceinline void Rva003B6680Vector::initialize_from(
	const Rva003B6680VectorBase &source)
{
	Rva003B6680VectorBase *sourceAccess =
		(Rva003B6680VectorBase *)&source;
	const Rva003B6680VectorBase *destinationAccess = this;
	const_cast<Rva003B6680VectorBase *>(destinationAccess)->initialize_base(
		(unsigned)(sourceAccess->m_finish - sourceAccess->m_start),
		sourceAccess->get_allocator());
	const_cast<Rva003B6680VectorBase *>(destinationAccess)->m_finish = copyVectorElements(
		sourceAccess->m_start, sourceAccess->m_finish, destinationAccess->m_start,
		Rva003B6680FalseType());
}

class Rva003B6680
{
public:
	virtual ~Rva003B6680();
	Rva003B6680(const Rva003B6680 &other);

private:
	Rva003B6680AsciiString m04;
	Rva003B6680Member08 m08;
	Rva003B6680Member14 m14;
	Rva003B6680Member20 m20;
	Rva003B6680Member2C m2c;
	Rva003B6680Member38 m38;
	Rva003B6680Member44 m44;
	Rva003B6680AsciiString m50;
	Rva003B6680Member54 m54;
	Rva003B6680Member60 m60;
	Rva003B6680Member6C m6c;
	Rva003B6680Member78 m78;
	Rva003B6680Member84 m84;
	Rva003B6680Member90 m90;
	Rva003B6680Member9C m9c;
	Rva003B6680Vector mA8;
	Rva003B6680MemberB4 mB4;
	Rva003B6680MemberC0 mC0;
	Rva003B6680MemberCC mCC;
	bool mD8;
};

// Ported from Open BFME 2 Code/GameEngine/Source/Common/System/Rva0056616BCopy.cpp.
Rva003B6680::Rva003B6680(const Rva003B6680 &other)
	: m04(other.m04)
	, m08(other.m08)
	, m14(other.m14)
	, m20(other.m20)
	, m2c(other.m2c)
	, m38(other.m38)
	, m44(other.m44)
	, m50(other.m50)
	, m54(other.m54)
	, m60(other.m60)
	, m6c(other.m6c)
	, m78(other.m78)
	, m84(other.m84)
	, m90(other.m90)
	, m9c(other.m9c)
	, mA8((mA8.initialize_from(other.mA8), 0))
	, mB4(other.mB4)
	, mC0(other.mC0)
	, mCC(other.mCC)
	, mD8(other.mD8)
{
}

// Retail 0x003A9F60: the inline element-copy vector constructor called by
// Rva003B6680 above. The explicit Coord3D copy preserves the +0x10 cursors.
// Donor: Open BFME 2 StlportCapturedBoneVectorCopy.cpp (0x00166110).
#include <vector>
#include "../../../Libraries/Include/Lib/Coord3D.h"
extern int R2Data010EC764;

// Existing retail allocation specialization and empty-allocator accessor.
struct Gen_t_003a7bf0_p32cd { unsigned char bytes[32]; };
class Gen_003a6710 { public: int m(int); };

struct Rva003A9F60Coord : Coord3D
{
    Rva003A9F60Coord(const Rva003A9F60Coord &other)
    {
        x = other.x;
        y = other.y;
        z = other.z;
    }
};

struct Rva003A9F60Element
{
    void *m_vptr;
    unsigned int m_at04;
    Rva003A9F60Coord m_position;
    float m_scalar;
    unsigned int m_at18;
    bool m_flag;

    Rva003A9F60Element(const Rva003A9F60Element &other)
        : m_vptr(&R2Data010EC764), m_at04(other.m_at04),
          m_position(other.m_position), m_scalar(other.m_scalar),
          m_at18(other.m_at18), m_flag(other.m_flag)
    {
    }
};

namespace _STL {
template<> _Vector_base<Gen_t_003a7bf0_p32cd,
    allocator<Gen_t_003a7bf0_p32cd> >::_Vector_base(
        unsigned int, const allocator<Gen_t_003a7bf0_p32cd> &);
}

class Rva003A9F60Vector
    : public _STL::_Vector_base<Gen_t_003a7bf0_p32cd,
                               _STL::allocator<Gen_t_003a7bf0_p32cd> >
{
    typedef _STL::allocator<Gen_t_003a7bf0_p32cd> Alloc;
    typedef Alloc (Gen_003a6710::*Accessor)() const;
public:
    Rva003A9F60Vector(const Rva003A9F60Vector &other)
        : _STL::_Vector_base<Gen_t_003a7bf0_p32cd, Alloc>(
              (unsigned)(other._M_finish - other._M_start),
              (((const Gen_003a6710 *)&other)->*
                  reinterpret_cast<Accessor>(&Gen_003a6710::m))())
    {
        const Rva003A9F60Element *last =
            (const Rva003A9F60Element *)other._M_finish;
        const Rva003A9F60Element *first =
            (const Rva003A9F60Element *)other._M_start;
        Rva003A9F60Element *out = (Rva003A9F60Element *)_M_start;
        while (first != last) {
            new (out) Rva003A9F60Element(*first);
            ++first;
            ++out;
        }
        _M_finish = (Gen_t_003a7bf0_p32cd *)out;
    }
};

void emitCopy003A9F60(void *out, const Rva003A9F60Vector &source)
{
    new (out) Rva003A9F60Vector(source);
}
