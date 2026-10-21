// ?_bfme_serviceHighestPriorityCheck@Eva@@AAEXXZ
// partial score=0.5132 date=2026-10-21
// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// readable body of ?update@Eva@@: game/GameEngine/Source/GameClient/Eva.cpp
// Open-BFME5: Eva::update, spelled against the retail BFME layout.
//
// BFME's Eva is not Zero Hour's.  Retail runs one countdown pair per live check
// record in milliseconds rather than tracking absolute frame numbers, and it
// only reaches for the next line when EVA is enabled, the audio manager exists,
// nothing is already speaking, and the logic has run more than two frames.  The
// Zero Hour GameClient/Eva.h describes none of that, so the class is spelled
// against the retail layout in its own translation unit (AGENTS.md,
// "Placement and integrity").
//
// Identity: slot 5 of the primary Eva vtable at 0x010F1FA8, whose slot 1 is the
// already matched ?init@Eva@@UAEXXZ region and slot 4 is the matched
// reset body ?reset@Eva@@UAEXXZ.  The +0x4c check vector, +0x58 speech handle and
// +0x5c enable flag are the same members ?setEvaEnabled@Eva@@QAEX_N@Z and
// Eva::reset touch.  The [vtable+0xB0] dispatch on TheAudio is the identical
// call the matched ?isCurrentlyPlaying@AudioEventRTS@@QBE_NXZ makes, which is
// what names it.

#include "ascii_string.h"

typedef bool Bool;
typedef int Int;
typedef unsigned int UnsignedInt;
typedef float Real;
typedef UnsignedInt AudioHandle;

// One logic frame at thirty frames a second, which is the step retail subtracts
// from both countdowns.
#define MSEC_PER_LOGICFRAME_REAL ( 1000.0f / 30.0f )

// __single_inheritance so the pointer-to-member below is the compact
// "just an address" representation retail compiled with; without it MSVC falls
// back to the general form and emits the whole vtordisp dance.
// STLport's red-black tree node walk; the side-sound map below is iterated
// node by node exactly as an inlined map iterator does.
namespace _STL
{
	struct _Rb_tree_node_base
	{
		int m_color;
		_Rb_tree_node_base *m_parent;
		_Rb_tree_node_base *m_left;
		_Rb_tree_node_base *m_right;
	};
	template <class Dummy> struct _Rb_global
	{
		static _Rb_tree_node_base * __cdecl _M_increment( _Rb_tree_node_base *node );
	};
}


struct Coord3D;
class AudioEventRTS
{
public:
	AudioEventRTS( const AsciiString &eventName, int owner );
	~AudioEventRTS();
	void setPlayerIndex( int playerIndex );
	void setPosition( const Coord3D *position );

private:
	char m_storage[ 0x70 ];
};

class __single_inheritance AudioManager;
extern AudioManager *TheAudio;
class AudioManagerSlots
{
public:
	virtual void slot00(); virtual void slot01(); virtual void slot02();
	virtual void slot03(); virtual void slot04(); virtual void slot05();
	virtual void slot06(); virtual void slot07(); virtual void slot08();
	virtual void slot09(); virtual void slot10(); virtual void slot11();
	virtual void slot12(); virtual void slot13(); virtual void slot14();
	virtual void slot15(); virtual void slot16();
	virtual AudioHandle addAudioEvent( const AudioEventRTS *event );	// +0x44
};

class Player
{
public:
	char m_head[ 0x24 ];
	int m_playerIndex;			// +0x24
	AsciiString m_side;			// +0x28
};
class PlayerList
{
public:
	char m_head[ 0x0c ];
	Player *m_local;			// +0x0c
};
extern PlayerList *ThePlayerList;

extern "C" __declspec(dllimport) int __cdecl _memicmp( const void *a, const void *b, unsigned int count );

// Only the frame counter at +0x3c is load-bearing here; retail reads it inline
// rather than calling an accessor.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/GameLogic.h
class GameLogic
{
public:
	UnsignedInt getFrame( void ) const { return m_frame; }

private:
	char        m_head[ 0x3c ];
	UnsignedInt m_frame;			// +0x3c
};

extern GameLogic *TheGameLogic;

// Retail per-message check record, 24 bytes: two millisecond countdowns and a
// played flag at +0x14.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameClient/Eva.h
class BfmeThingYQ;
class Vector3YQ;
struct EvaCheck
{
	Real m_timeUntilExpire;
	Real m_timeUntilNextCheck;
	char m_rest[ 0x10 ];
};
// The matched anchor helper at 0x00423300 (ILT 0x00025077), named by its
// existing ledger spelling; it reads the check record for the player.
class Gen_00423300
{
public:
	Vector3YQ *bfmeAnchorYQ( BfmeThingYQ *player );
};

// Side-sound map node: the side name keys a sound entry; the entry's data is
// read directly (+0x84 kind, +0x38 flags) to decide whether the line plays
// at the check's anchor.
struct EvaSoundData
{
	char m_head[ 0x38 ];
	unsigned int m_flags;			// +0x38
	char m_pad[ 0x48 ];
	int m_kind;				// +0x84
};
struct EvaSideSoundNode : public _STL::_Rb_tree_node_base
{
	AsciiString m_side;			// +0x10
	AsciiString m_sound;			// +0x14
};

// Retail parsed check-info record, 28 bytes: three counts, the priority at
// +0x0c and the side-sound map whose header node pointer is at +0x10.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameClient/Eva.h
struct EvaCheckInfo
{
	UnsignedInt m_u00;
	UnsignedInt m_u04;
	UnsignedInt m_u08;
	UnsignedInt m_priority;			// +0x0c
	EvaSideSoundNode *m_sideSounds;		// +0x10 map header node
	char m_mapRest[ 8 ];
};

class EvaCheckInfoVec
{
public:
	Int size( void ) const { return m_end - m_begin; }

	EvaCheckInfo *m_begin;
	EvaCheckInfo *m_end;
	EvaCheckInfo *m_capacity;
};

class EvaCheckVec
{
public:
	Int size( void ) const { return m_end - m_begin; }

	EvaCheck *m_begin;
	EvaCheck *m_end;
	EvaCheck *m_capacity;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameClient/Eva.h
class Eva
{
public:
	// Slot 5 of the primary vtable at 0x010F1FA8; virtual so the body carries
	// retail's ?update@Eva@@UAEXXZ decoration and the +0x00 vtable pointer lands
	// where retail's does.
	virtual void update( void );

private:
	// 0x004237E0 through the ILT entry at 0x0000F32B: walks the check-info table
	// and starts the highest-priority pending line.  Retail never named it.
	void _bfme_serviceHighestPriorityCheck( void );

	char            m_head[ 0x08 ];		// +0x04 pad and the +0x08 vtable pointer
	EvaCheckInfoVec m_checkInfos;		// +0x0c
	EvaCheckInfoVec m_defaultCheckInfos;	// +0x18
	char            m_sideSounds[ 0x28 ];	// +0x24 the two side-sound containers
	EvaCheckVec     m_checks;		// +0x4c
	AudioHandle     m_speechHandle;		// +0x58
	Bool            m_enabled;		// +0x5c
};

void Eva::update( void )
{
	// The live records and the parsed table are built together; a mismatch means
	// nothing has been parsed yet.
	if( m_checks.size() != m_checkInfos.size() )
		return;

	if( m_enabled && TheAudio != 0 )
	{
		typedef Bool (AudioManager::*IsCurrentlyPlayingProc)( AudioHandle );
		if( !(TheAudio->**(IsCurrentlyPlayingProc *)(*(char **)TheAudio + 0xB0))( m_speechHandle )
				&& TheGameLogic->getFrame() > 2 )
		{
			_bfme_serviceHighestPriorityCheck();
		}
	}

	// Both countdowns run whether or not anything was started this frame.
	EvaCheck *check = m_checks.m_begin;
	EvaCheck *last = m_checks.m_end;
	while( check != last )
	{
		check->m_timeUntilExpire -= MSEC_PER_LOGICFRAME_REAL;
		check->m_timeUntilNextCheck -= MSEC_PER_LOGICFRAME_REAL;
		++check;
	}
}

// Retail inlines this length-limited, case-insensitive comparison.
static inline int compareSideNoCase( const AsciiString &side, const AsciiString &key )
{
	int keyLength = key.getLength();
	const char *keyText = key.str();
	int sideLength = side.getLength();
	const char *sideText = side.str();
	int result = _memicmp( sideText, keyText,
		sideLength < keyLength ? sideLength : keyLength );
	if( result != 0 )
		return result;
	return sideLength - keyLength;
}

// 0x004237E0 (719 bytes), reached from update() through ILT 0x0000F32B: picks
// the pending check with the highest priority, earliest by its countdown,
// rearms it, and plays its line for the local player's side. A line that
// fails to start (handle below 5) leaves the loop to try the next candidate.
void Eva::_bfme_serviceHighestPriorityCheck( void )
{
	Bool retry;
	do
	{
		Int best = -1;
		struct { UnsignedInt priority; Real time; } bestSoFar;
		bestSoFar.priority = 0;
		bestSoFar.time = 0;
		EvaCheck *checks;
		for( UnsignedInt i = 0; i < (UnsignedInt)m_checkInfos.size(); ++i )
		{
			checks = m_checks.m_begin;
			EvaCheck &check = checks[ i ];
			if( check.m_timeUntilNextCheck >= 0.0f )
			{
				const EvaCheckInfo *infos = m_checkInfos.m_begin;
				UnsignedInt priority = infos[ i ].m_priority;
				Real t = (Real)infos[ i ].m_u04 - check.m_timeUntilNextCheck;
				if( best == -1 || priority > bestSoFar.priority
						|| ( priority == bestSoFar.priority && t < bestSoFar.time ) )
				{
					bestSoFar.time = t;
					best = i;
					bestSoFar.priority = priority;
				}
			}
		}
		if( best == -1 )
			return;

		const EvaCheckInfo *info = &m_checkInfos.m_begin[ best ];
		EvaCheck *check = &checks[ best ];
		check->m_timeUntilNextCheck = -1.0f;
		const UnsignedInt &expire = info->m_u00 < info->m_u08 ? info->m_u08 : info->m_u00;
		check->m_timeUntilExpire = (Real)expire;

		retry = true;
		Player *local = ThePlayerList->m_local;
		if( local == 0 )
			return;

		AsciiString side( local->m_side );
		_STL::_Rb_tree_node_base *end = info->m_sideSounds;
		_STL::_Rb_tree_node_base *node = end->m_left;
		while( node != end )
		{
			const AsciiString &key = ((EvaSideSoundNode *)node)->m_side;
			if( compareSideNoCase( side, key ) == 0 )
				break;
			node = _STL::_Rb_global<bool>::_M_increment( node );
		}
		if( node != end )
		{
			const AsciiString &sound = ((EvaSideSoundNode *)node)->m_sound;
			if( *(void *const *)&sound != 0 )
			{
				AudioEventRTS event( sound, 0 );
				event.setPlayerIndex( local->m_playerIndex );
				const EvaSoundData *data = *(const EvaSoundData *const *)&sound;
				if( data->m_kind == 3 || ( data->m_kind == 2 && ( data->m_flags & 2 ) ) )
					event.setPosition( (const Coord3D *)
						((Gen_00423300 *)check)->bfmeAnchorYQ( (BfmeThingYQ *)local ) );
				m_speechHandle = ((AudioManagerSlots *)TheAudio)->addAudioEvent( &event );
				if( m_speechHandle >= 5 )
					retry = false;
			}
		}
	}
	while( retry );
}
