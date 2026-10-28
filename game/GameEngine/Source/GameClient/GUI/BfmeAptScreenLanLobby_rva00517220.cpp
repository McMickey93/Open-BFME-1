// cl: /DNDEBUG /MD /EHsc /Iinputs/reference/shims/stringinline
// Retail 0x00517220, 241 bytes: slot 14 of BfmeAptScreenLanLobby's vtable,
// installed by the matched constructor at 0x00519F90.  With a true argument
// it raises the "QM:STARTINGGAME" message box (style 3, "APT:None" title)
// through the matched bfmeMakeZB and then asks TheLAN for one of two
// requests; otherwise it hands 1 to the routine behind the
// ReleaseWindowLayout incremental-link thunk.  The member name and the
// LANAPI slots are unrecorded, so they keep their addresses and offsets.

#include "StringInline.h"

class GameTextInterface
{
public:
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual void slot0C(); virtual void slot10(); virtual void slot14();
	virtual void slot18(); virtual void slot1C(); virtual void slot20();
	virtual void slot24();
	virtual UnicodeString fetch( const char *label, bool *exists = 0 );
};
extern GameTextInterface *TheGameText;

class LANAPI
{
public:
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual void slot0C(); virtual void slot10(); virtual void slot14();
	virtual void slot18(); virtual void slot1C(); virtual void slot20();
	virtual void slot24(); virtual void slot28(); virtual void slot2C();
	virtual void slot30(); virtual void slot34();
	virtual void slot38();
	virtual void slot3C(); virtual void slot40();
	virtual void slot44( int value );
	virtual void slot48(); virtual void slot4C(); virtual void slot50();
	virtual void slot54(); virtual void slot58(); virtual void slot5C();
	virtual void slot60(); virtual void slot64(); virtual void slot68();
	virtual void slot6C(); virtual void slot70(); virtual void slot74();
	virtual void slot78(); virtual void slot7C(); virtual void slot80();
	virtual void slot84(); virtual void slot88(); virtual void slot8C();
	virtual void slot90(); virtual void slot94(); virtual void slot98();
	virtual void slot9C(); virtual void slotA0(); virtual void slotA4();
	virtual void slotA8(); virtual void slotAC(); virtual void slotB0();
	virtual void slotB4();
	virtual bool slotB8();
};
extern LANAPI *TheLAN;

class WindowLayout;
void ReleaseWindowLayout( WindowLayout *layout );

// The matched message-box builder at 0x00522DD0 takes the style and the two
// strings by address.
void __cdecl bfmeMakeZB( void *first, void *second, void *third );
typedef void (__cdecl *BfmeLanLobbyMessageBox)( int style, const UnicodeString &title,
	const UnicodeString &body );

class BfmeAptScreenLanLobby
{
public:
	void rva00517220( bool show );
};

// ?rva00517220@BfmeAptScreenLanLobby@@QAEX_N@Z
void BfmeAptScreenLanLobby::rva00517220( bool show )
{
	if( show )
	{
		((BfmeLanLobbyMessageBox)bfmeMakeZB)( 3, TheGameText->fetch( "APT:None" ),
			TheGameText->fetch( "QM:STARTINGGAME" ) );
		if( TheLAN )
		{
			if( TheLAN->slotB8() )
				TheLAN->slot44( 0 );
			else
				TheLAN->slot38();
		}
	}
	else
		ReleaseWindowLayout( (WindowLayout *)1 );
}
