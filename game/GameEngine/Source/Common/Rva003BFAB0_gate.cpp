// cl: /DNDEBUG /MD /EHsc
//
// Rva003BFAB0::run, retail 0x003BFAB0, 87 bytes.
//
// Sibling of Rva003BFB20::run on d_003b8450: always probe(m_at28, &m_at30) into
// m_at80; on a false stack flag write the +0xC8/+0xCC/+0x78/+0x7C fail block and
// return; otherwise on probe success step the campaign manager and finish().

class Glo012F1024Type
{
public:
	void step();
};

// Retail's global at 0x012F1024 is EA's LivingWorldCampaignManager singleton,
// defined once in GameEngine/Source/GameLogic/LivingWorld/
// LivingWorldCampaignManager.cpp, so this reference carries that canonical type
// (class, not struct); the local view above is cast in at the one use.
class LivingWorldCampaignManager;

extern LivingWorldCampaignManager *TheLivingWorldCampaignManager;

class Gen003BFB20Owner
{
public:
	bool probe( void * key );
};

class Rva003BFAB0
{
public:
	void run( bool flag );

private:
	char m_pad00[ 0x28 ];
	Gen003BFB20Owner *m_at28;
	char m_pad2C[ 0x4 ];
	char m_at30;
	char m_pad31[ 0x78 - 0x31 ];
	bool m_at78;
	char m_pad79[ 0x7C - 0x79 ];
	int m_at7C;
	bool m_at80;
	char m_pad81[ 0xC8 - 0x81 ];
	bool m_atC8;
	char m_padC9[ 0xCC - 0xC9 ];
	int m_atCC;
};

// finish() is reached through ILT 0x0000A754, the ledger's 5-byte row
// ?j_0000a754@@YAXXZ (symbols.csv pins ?finish@Rva003BFAB0@@QAEXXZ there and
// nothing defines it), through a raw pointer bridge that keeps the thiscall
// shape.
void j_0000a754();

// ?run@Rva003BFAB0@@QAEX_N@Z
void Rva003BFAB0::run( bool flag )
{
	bool ok = m_at28->probe( &m_at30 );
	m_at80 = ok;
	if( !flag )
	{
		m_atC8 = true;
		m_atCC = 0x78;
		m_at78 = true;
		m_at7C = 0x1E;
		return;
	}
	if( ok )
	{
		((Glo012F1024Type *)TheLivingWorldCampaignManager)->step();
		union { void (*raw)( void ); void (Rva003BFAB0::*typed)( void ); } finish;
		finish.raw = &j_0000a754;
		(this->*finish.typed)();
	}
}
