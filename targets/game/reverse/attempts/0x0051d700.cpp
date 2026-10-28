// ?rva0051D700@BfmeAptScreenMainMenu@@QAEHXZ
// partial score=0.7996 date=2026-10-28
// cl: /DNDEBUG /MD /EHsc /Iinputs/reference/shims/stringinline
// Retail 0x0051D700, 484 bytes: slots 5 and 6 of BfmeAptScreenMainMenu's
// vtable (0x011061C4, through ILT 0x000026A8), installed by the matched
// constructor at 0x0051F3A0.  It steps the main menu's pending state at
// +0x264: state 1 hides the shell and, when the "00000000.sav" check passes,
// restarts the engine side and shows the shell again (otherwise moves to
// state 2); state 4 refreshes the credits sink and hides the credits
// movie; state 5 runs the firewall helper at +0x268 and either starts
// multiplayer or raises the no-admin message box, then like state 6 clears
// the state.  The member name is unrecorded and keeps the address.
#include "StringInline.h"

class GameWindow;

class Shell
{
public:
	void hide( bool hide );
	void showShell( bool runInit );
};
extern Shell *TheShell;

enum SaveCode { SC_OK };
class GameState
{
public:
	SaveCode rva001127F0( const AsciiString &filename );
};
extern GameState *TheGameState;

class GameEngine
{
public:
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual void slot0C();
	virtual void slot10();
};
extern GameEngine *TheGameEngine;

class BfmeSinkBOE
{
public:
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual void slot0C(); virtual void slot10();
	virtual void slot14();
	unsigned char m_unmodelled04[0x2C];
	bool m_rva30;
};
extern BfmeSinkBOE *g_bfmeSinkBOE;

class BfmeLevelAN
{
public:
	char *bfmeBuildAN( unsigned int movie, int name, int a, int b, int c, int d, int e, int f );
};
class WindowManager
{
public:
	void bfme_hideBackground( bool hide );
};
struct Rva00579160Manager;
extern Rva00579160Manager *Rva00579160TheManager;

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

void GSMessageBoxOk( UnicodeString title, UnicodeString message, void (*okFunc)( void ) );

class Rva00690CB0Owner
{
public:
	bool init();
};

class BfmeAptScreenMainMenu
{
public:
	int rva0051D700();

private:
	unsigned char m_unmodelled000[0x250];
	unsigned int m_movie;
	unsigned char m_unmodelled254[5];
	bool m_rva259;
	unsigned char m_unmodelled25A[0xA];
	int m_state;
	Rva00690CB0Owner m_firewall;
};

// ?rva0051D700@BfmeAptScreenMainMenu@@QAEHXZ
int BfmeAptScreenMainMenu::rva0051D700()
{
	switch( m_state )
	{
		case 1:
		{
			TheShell->hide( true );
			bool found = TheGameState->rva001127F0( AsciiString( "00000000.sav" ) ) != 0;
			if( found )
			{
				TheGameEngine->slot10();
				TheShell->showShell( true );
				m_rva259 = false;
				m_state = 0;
				((WindowManager *)Rva00579160TheManager)->bfme_hideBackground( false );
			}
			else
				m_state = 2;
			break;
		}

		case 4:
			if( g_bfmeSinkBOE )
			{
				g_bfmeSinkBOE->slot14();
				if( g_bfmeSinkBOE->m_rva30 )
					((BfmeLevelAN *)Rva00579160TheManager)->bfmeBuildAN( m_movie, (int)"HideCredits", 0, 0, 0, 0, 0, 0 );
			}
			break;

		case 5:
			if( !m_firewall.init() )
			{
				((BfmeLevelAN *)Rva00579160TheManager)->bfmeBuildAN( m_movie, (int)"FirewallMessageClose", 0, 0, 0, 0, 0, 0 );
				GSMessageBoxOk( TheGameText->fetch( "GUI:FirewallNoAdminTitle" ),
					TheGameText->fetch( "GUI:FirewallNoAdminMessage" ), 0 );
			}
			else
				((BfmeLevelAN *)Rva00579160TheManager)->bfmeBuildAN( m_movie, (int)"FirewallMessageClose", 1, (int)"startMulti", 0, 0, 0, 0 );
			// fall through
		case 6:
			m_state = 0;
			break;
	}
	return 1;
}
