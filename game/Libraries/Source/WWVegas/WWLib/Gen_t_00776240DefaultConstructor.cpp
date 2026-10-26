// cl: /DNDEBUG /DWIN32 /D_WINDOWS /D_STLP_USE_STATIC_LIB /DBFME_STLP_NODE_ALLOC /MD /EHsc /Iinputs/reference/shims/stlp_nodealloc /Iinputs/reference/shims/w3dmodeldraw /Iinputs/reference/shims/asciistring8 /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad
// stlport

#include "PreRTS.h"
#include "W3DDevice/GameClient/Module/W3DModelDraw.h"
#include <new>
#include <vector>

// Small node allocations go through STLport's __node_alloc<true, 0>; its
// inline allocate() reaches _M_allocate (retail 0x0082E540) for sizes
// up to _MAX_BYTES.

extern "C" void *memset( void *destination, int value, unsigned int count );

class BFMERetailAsciiString
{
public:
	BFMERetailAsciiString() : m_data( 0 ) {}
	~BFMERetailAsciiString();

private:
	void *m_data;
};

struct Raw10
{
	Raw10()
	{
		memset( this, 0, 0x28 );
	}

	unsigned int words[ 10 ];
};

struct Rva00776240List50
{
	Rva00776240List50() : m_head( 0 )
	{
		void *head = _STL::__node_alloc<true, 0>::allocate( 0x2c );
		*( (void **)head ) = head;
		*( (void **)( (unsigned char *)head + 4 ) ) = head;
		m_head = head;
	}
	~Rva00776240List50();

	void *m_head;
};

struct Rva00776240Vector54
{
	Rva00776240Vector54()
	{
		m_body[ 0 ] = 0;
		m_body[ 1 ] = 0;
		m_body[ 2 ] = 0;
	}
	~Rva00776240Vector54();

	unsigned int m_body[ 3 ];
};

struct Rva00776240Vector60
{
	Rva00776240Vector60()
	{
		m_body[ 0 ] = 0;
		m_body[ 1 ] = 0;
		m_body[ 2 ] = 0;
	}
	~Rva00776240Vector60();

	unsigned int m_body[ 3 ];
};

typedef PristineBoneInfoMap Rva00776240Vector70;

struct Rva00776240Field7C
{
	Rva00776240Field7C();
	~Rva00776240Field7C();
	unsigned int m_body[ 3 ];
};

#pragma comment(linker, "/alternatename:??0Rva00776240Field7C@@QAE@XZ=?j_00018647@@YAXXZ")
#pragma comment(linker, "/alternatename:??1Rva00776240Field7C@@QAE@XZ=?j_000455e8@@YAXXZ")

struct Rva00776240ByteAC
{
	Rva00776240ByteAC() : m_value( 0 )
	{
	}
	~Rva00776240ByteAC()
	{
	}

	unsigned char m_value;
};

struct Rva00776240FieldB0
{
	Rva00776240FieldB0()
	{
		m_words[ 0 ] = 0;
		m_words[ 1 ] = 0;
		m_words[ 2 ] = 0;
	}
	~Rva00776240FieldB0();

	unsigned int m_words[ 3 ];
};

struct Rva00776240Vector2CElement
{
	char m_body[ 0x38 ];
};

class Gen_t_00776240_p128pod : public BFMERetailAsciiString
{
	public:
	// ??0Gen_t_00776240_p128pod@@QAE@XZ
	Gen_t_00776240_p128pod();

private:
	Raw10 m_raw;
	_STL::vector< Rva00776240Vector2CElement > m_vector2C;
	unsigned int m_dword38;
	unsigned int m_dword3C;
	unsigned char m_byte40;
	unsigned int m_dword44;
	BFMERetailAsciiString m_string48;
	unsigned int m_dword4C;
	Rva00776240List50 m_list50;
	Rva00776240Vector54 m_vector54;
	Rva00776240Vector60 m_vector60;
	unsigned char m_byte6C;
	char m_padding6D[ 3 ];
	Rva00776240Vector70 m_vector70;
	Rva00776240Field7C m_vector7C[ 4 ];
	Rva00776240ByteAC m_byteAC;
	Rva00776240FieldB0 m_fieldB0;
};

// ??0Gen_t_00776240_p128pod@@QAE@XZ
Gen_t_00776240_p128pod::Gen_t_00776240_p128pod()
	: BFMERetailAsciiString(),
	  m_raw(),
	  m_vector2C(),
	  m_dword38( 0 ),
	  m_dword3C( 0 ),
	  m_byte40( 0 ),
	  m_dword44( 0 ),
	  m_string48(),
	  m_dword4C( 0xffffffff ),
	  m_list50(),
	  m_vector54(),
	  m_vector60(),
	  m_byte6C(),
	  m_vector70(),
	  m_byteAC(),
	  m_fieldB0()
{
}