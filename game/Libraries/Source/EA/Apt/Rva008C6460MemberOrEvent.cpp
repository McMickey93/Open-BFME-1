// cl: /DNDEBUG /MD /EHsc
// Retail 0x008C6460 (94 B): a file-static Apt helper. For a defined object whose type
// code (flags +0x04, low six bits) lies in 12..19, types 13 and 18 forward the member
// store to the registry flag setter 0x008AD350 and type 14 to the event-bit setter
// 0x008D30D0, both on the object's +0x50 owner with (name, object, value). Its only
// direct callers sit in the still-dumped body at 0x008CC690 (two calls), so its name stays
// address-derived; as a file-static it takes the object in ESI, the name in EBX and the
// value in EDI, retail's private convention.

struct BfmeString008AD350;
struct Rva008D30D0String;

class BfmeObject008AD350
{
public:
	void setMember( BfmeString008AD350 *name, void *object, int value );
};

class Rva008D30D0Owner
{
public:
	void setEvent( Rva008D30D0String *name, void *object, int value );
};

struct Rva008C6460Object
{
	void *m_vtable;
	unsigned int m_flags;			// +0x04: type code in bits 0..5, defined in bit 15
	unsigned char m_pad08[ 0x48 ];
	void *m_owner;					// +0x50
};

// ?rva008C6460@@YAXPAURva008C6460Object@@PAUBfmeString008AD350@@H@Z
static __declspec(noinline) void rva008C6460( Rva008C6460Object *object,
	BfmeString008AD350 *name, int value )
{
	unsigned int flags = object->m_flags;
	int kind = flags & 0x3f;
	if( kind >= 12 && kind <= 19 && ( static_cast<unsigned char>( ~( flags >> 15 ) ) & 1 ) == 0 &&
		( kind == 13 || kind == 18 ) )
		static_cast<BfmeObject008AD350 *>( object->m_owner )->setMember( name, object, value );
	flags = object->m_flags;
	kind = flags & 0x3f;
	if( kind >= 12 && kind <= 19 && ( static_cast<unsigned char>( ~( flags >> 15 ) ) & 1 ) == 0 &&
		kind == 14 )
		static_cast<Rva008D30D0Owner *>( object->m_owner )->setEvent(
			reinterpret_cast<Rva008D30D0String *>( name ), object, value );
}

// ?rva008C6460Caller@@YAXPAURva008C6460Object@@PAUBfmeString008AD350@@H@Z absent-from-retail
// TU-local caller that keeps the static above alive.
void rva008C6460Caller( Rva008C6460Object *object, BfmeString008AD350 *name, int value )
{
	rva008C6460( object, name, value );
}
