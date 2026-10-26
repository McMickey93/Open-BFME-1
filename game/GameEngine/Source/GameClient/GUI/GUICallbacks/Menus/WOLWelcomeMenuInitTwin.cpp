// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/stringbaseunicode /Iinputs/reference/shims/campaignmanagerascii /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameNetwork /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Benchmark /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWAudio /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Igame/Libraries/Source/WWVegas/WWLib
// stlport
#define Matrix4x4 Matrix4  // BFME renamed it
#define __SHELL_H_
#define __PLACEMENT_VEC_NEW_INLINE  // always.h/GameMemory.h define array placement-new themselves
/*
**	Command & Conquer Generals Zero Hour(tm)
**	Copyright 2025 Electronic Arts Inc.
**
**	This program is free software: you can redistribute it and/or modify
**	it under the terms of the GNU General Public License as published by
**	the Free Software Foundation, either version 3 of the License, or
**	(at your option) any later version.
**
**	This program is distributed in the hope that it will be useful,
**	but WITHOUT ANY WARRANTY; without even the implied warranty of
**	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**	GNU General Public License for more details.
**
**	You should have received a copy of the GNU General Public License
**	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

////////////////////////////////////////////////////////////////////////////////
//																																						//
//  (c) 2001-2003 Electronic Arts Inc.																				//
//																																						//
////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////////////
// FILE: WOLWelcomeMenu.cpp
// Author: Chris Huybregts, November 2001
// Description: Lan Lobby Menu
///////////////////////////////////////////////////////////////////////////////////////

// INCLUDES ///////////////////////////////////////////////////////////////////////////////////////
#include "PreRTS.h"	// This must go first in EVERY cpp file int the GameEngine

#include "GameSpy/peer/peer.h"

#include "Common/GameEngine.h"
#include "Common/GameSpyMiscPreferences.h"
#include "Common/CustomMatchPreferences.h"
#include "Common/GlobalData.h"
#include "Common/UserPreferences.h"
#include "Common/PlayerTemplate.h"

#include "GameClient/AnimateWindowManager.h"
#include "GameClient/Display.h"
#include "GameClient/WindowLayout.h"
#include "GameClient/Gadget.h"
#include "GameClient/GameText.h"
// BFME returns Bool; the vendored Zero Hour Shell declaration returns void.
// Keep this corrected ABI local, as in SinglePlayerMenu.cpp.
class Shell
{
public:
	Bool showShellMap(Bool useShellMap);
};
extern Shell *TheShell;
#include "GameClient/KeyDefs.h"
#include "GameClient/GameWindowManager.h"
#include "GameClient/GadgetListBox.h"
#include "GameClient/GadgetTextEntry.h"
#include "GameClient/GadgetStaticText.h"
#include "GameClient/GadgetCheckBox.h"
#include "GameClient/MessageBox.h"
#include "GameClient/GameWindowTransitions.h"

#include "GameNetwork/FirewallHelper.h"
#include "GameNetwork/GameSpyOverlay.h"

#include "GameNetwork/GameSpy/BuddyDefs.h"
#define BuddyRequest Rva0050D030ReferenceBuddyRequest
#define GameSpyBuddyMessageQueueInterface Rva0050D030ReferenceBuddyMessageQueueInterface
#include "GameNetwork/GameSpy/BuddyThread.h"
#undef GameSpyBuddyMessageQueueInterface
#undef BuddyRequest
#include "GameNetwork/GameSpy/PeerDefs.h"
#define PeerRequest Rva0050D030ReferencePeerRequest
#define GameSpyPeerMessageQueueInterface Rva0050D030ReferencePeerMessageQueueInterface
#include "GameNetwork/GameSpy/PeerThread.h"
#undef GameSpyPeerMessageQueueInterface
#undef PeerRequest
#include "GameNetwork/GameSpy/PersistentStorageDefs.h"
#include "GameNetwork/GameSpy/PersistentStorageThread.h"
#include "GameNetwork/GameSpy/BuddyThread.h"
#include "GameNetwork/GameSpy/ThreadUtils.h"
#include "GameNetwork/GameSpy/MainMenuUtils.h"
#include "GameNetwork/WOLBrowser/WebBrowser.h"

// Retail inlines ~UnicodeString: temporaries are released by a direct call to
// StringBase<unsigned short>::releaseBuffer (0x008881D0), not the ??1UnicodeString stub.
inline UnicodeString::~UnicodeString() { ((StringBase<unsigned short> *)this)->releaseBuffer(); }

// WindowLayout visibility is dispatched through its retail virtual slot.
class BfmeVirtualHideLayout
{
public:
	virtual void slot0() = 0;
	virtual void slot4() = 0;
	virtual void slot8() = 0;
	virtual void slotC() = 0;
	virtual void hide( Bool immediate ) = 0;
};


inline AsciiString::~AsciiString() { ((StringBase<char> *)this)->releaseBuffer(); }

class Rva0050C160GameSpyInfoView {
public:
    virtual void slot00() = 0;
    virtual void slot01() = 0;
    virtual void slot02() = 0;
    virtual void slot03() = 0;
    virtual void slot04() = 0;
    virtual Bool gotGroupRoomList() = 0;
    virtual void slot06() = 0;
    virtual void slot07() = 0;
    virtual void slot08() = 0;
    virtual void slot09() = 0;
    virtual void slot0A() = 0;
    virtual void slot0B() = 0;
    virtual void slot0C() = 0;
    virtual void slot0D() = 0;
    virtual void slot0E() = 0;
    virtual void slot0F() = 0;
    virtual void slot10() = 0;
    virtual void slot11() = 0;
    virtual void slot12() = 0;
    virtual void slot13() = 0;
    virtual void slot14() = 0;
    virtual void slot15() = 0;
    virtual void slot16() = 0;
    virtual void slot17() = 0;
    virtual void slot18() = 0;
    virtual void slot19() = 0;
    virtual void slot1A() = 0;
    virtual void slot1B() = 0;
    virtual void slot1C() = 0;
    virtual void slot1D() = 0;
    virtual void slot1E() = 0;
    virtual void slot1F() = 0;
    virtual void slot20() = 0;
    virtual void slot21() = 0;
    virtual AsciiString getLocalBaseName() = 0;
};
static Bool isShuttingDown = FALSE;
static Bool buttonPushed = FALSE;
static char *nextScreen = NULL;

// window ids ------------------------------------------------------------------------------
static NameKeyType parentWOLWelcomeID = NAMEKEY_INVALID;
static NameKeyType buttonBackID = NAMEKEY_INVALID;
static NameKeyType buttonQuickMatchID = NAMEKEY_INVALID;
static NameKeyType buttonLobbyID = NAMEKEY_INVALID;
static NameKeyType buttonBuddiesID = NAMEKEY_INVALID;
static NameKeyType buttonLadderID = NAMEKEY_INVALID;
static NameKeyType buttonMyInfoID = NAMEKEY_INVALID;

static NameKeyType listboxInfoID = NAMEKEY_INVALID;
static NameKeyType buttonOptionsID = NAMEKEY_INVALID;
// Window Pointers ------------------------------------------------------------------------
static GameWindow *parentWOLWelcome = NULL;
static GameWindow *buttonBack = NULL;
static GameWindow *buttonQuickMatch = NULL;
static GameWindow *buttonLobby = NULL;
static GameWindow *buttonBuddies = NULL;
static GameWindow *buttonLadder = NULL;
static GameWindow *buttonMyInfo = NULL;
static GameWindow *buttonbuttonOptions = NULL;
static WindowLayout *welcomeLayout = NULL;
static GameWindow *listboxInfo = NULL;

static GameWindow *staticTextServerName = NULL;
static GameWindow *staticTextLastUpdated = NULL;

static GameWindow *staticTextLadderWins = NULL;
static GameWindow *staticTextLadderLosses = NULL;
static GameWindow *staticTextLadderRank = NULL;
static GameWindow *staticTextLadderPoints = NULL;
static GameWindow *staticTextLadderDisconnects = NULL;

static GameWindow *staticTextHighscoreWins = NULL;
static GameWindow *staticTextHighscoreLosses = NULL;
static GameWindow *staticTextHighscoreRank = NULL;
static GameWindow *staticTextHighscorePoints = NULL;

static UnicodeString gServerName;
// ?enableControls@@YAX_N@Z absent-from-retail
static inline void enableControls( Bool state )
{
	if (buttonQuickMatch)
		buttonQuickMatch->winEnable(state);
	if (buttonLobby)
		buttonLobby->winEnable(state);
}

//-------------------------------------------------------------------------------------------------
/** This is called when a shutdown is complete for this menu */
//-------------------------------------------------------------------------------------------------

extern void updateNumPlayersOnline();
extern void updateOverallStats();
static Bool raiseMessageBoxes = FALSE;
//-------------------------------------------------------------------------------------------------
/** Initialize the WOL Welcome Menu */
//-------------------------------------------------------------------------------------------------
namespace Rva0050C160Twin
{
// ?WOLWelcomeMenuInit@Rva0050C160Twin@@YAXPAVWindowLayout@@PAX@Z
void WOLWelcomeMenuInit( WindowLayout *layout, void *userData )
{
	nextScreen = NULL;
	buttonPushed = FALSE;
	isShuttingDown = FALSE;

	welcomeLayout = layout;

	//TheWOL->reset();

	parentWOLWelcomeID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:WOLWelcomeMenuParent" ) );
	buttonBackID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:ButtonBack" ) );
	parentWOLWelcome = TheWindowManager->winGetWindowFromId( NULL, parentWOLWelcomeID );
	buttonBack = TheWindowManager->winGetWindowFromId( NULL,  buttonBackID);
	buttonOptionsID = TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:ButtonOptions" );
	buttonbuttonOptions = TheWindowManager->winGetWindowFromId( NULL,  buttonOptionsID);
	listboxInfoID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:InfoListbox" ) );

	listboxInfo = TheWindowManager->winGetWindowFromId( NULL,  listboxInfoID);

	staticTextServerName = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextServerName" ));
	staticTextLastUpdated = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextLastUpdated" ));

	staticTextLadderWins = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextLadderWins" ));
	staticTextLadderLosses = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextLadderLosses" ));
	staticTextLadderPoints = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextLadderPoints" ));
	staticTextLadderRank = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextLadderRank" ));
	staticTextLadderDisconnects = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextDisconnects" ));

	staticTextHighscoreWins = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextHighscoreWins" ));
	staticTextHighscoreLosses = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextHighscoreLosses" ));
	staticTextHighscorePoints = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextHighscorePoints" ));
	staticTextHighscoreRank = TheWindowManager->winGetWindowFromId( parentWOLWelcome,
		TheNameKeyGenerator->nameToKey( "WOLWelcomeMenu.wnd:StaticTextHighscoreRank" ));

	if (staticTextServerName)
	{
		GadgetStaticTextSetText(staticTextServerName, gServerName);
	}

	GameWindow *staticTextTitle = TheWindowManager->winGetWindowFromId(parentWOLWelcome, NAMEKEY("WOLWelcomeMenu.wnd:StaticTextTitle"));
	if (staticTextTitle && TheGameSpyInfo)
	{
		UnicodeString title;
		title.format(TheGameText->fetch("GUI:WOLWelcome"), ((Rva0050C160GameSpyInfoView *)TheGameSpyInfo)->getLocalBaseName().str());
		GadgetStaticTextSetText(staticTextTitle, title);
	}

	// Clear some defaults
	/*
	UnicodeString questionMark = UnicodeString(L"?");
	GadgetStaticTextSetText(staticTextLastUpdated, questionMark);
	GadgetStaticTextSetText(staticTextLadderWins, questionMark);
	GadgetStaticTextSetText(staticTextLadderLosses, questionMark);
	GadgetStaticTextSetText(staticTextLadderPoints, questionMark);
	GadgetStaticTextSetText(staticTextLadderRank, questionMark);
	GadgetStaticTextSetText(staticTextLadderDisconnects, questionMark);
	GadgetStaticTextSetText(staticTextHighscoreWins, questionMark);
	GadgetStaticTextSetText(staticTextHighscoreLosses, questionMark);
	GadgetStaticTextSetText(staticTextHighscorePoints, questionMark);
	GadgetStaticTextSetText(staticTextHighscoreRank, questionMark);
	*/

	//DEBUG_ASSERTCRASH(listboxInfo, ("No control found!"));

	buttonQuickMatchID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:ButtonQuickMatch" ) );
	buttonQuickMatch = TheWindowManager->winGetWindowFromId( parentWOLWelcome, buttonQuickMatchID );

	buttonLobbyID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:ButtonCustomMatch" ) );
	buttonLobby = TheWindowManager->winGetWindowFromId( parentWOLWelcome, buttonLobbyID );

	buttonBuddiesID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:ButtonBuddies" ) );
	buttonBuddies = TheWindowManager->winGetWindowFromId( parentWOLWelcome, buttonBuddiesID );

	buttonMyInfoID = TheNameKeyGenerator->nameToKey( AsciiString( "WOLWelcomeMenu.wnd:ButtonMyInfo" ) );
	buttonMyInfo = TheWindowManager->winGetWindowFromId( parentWOLWelcome, buttonMyInfoID );


	if (TheFirewallHelper == NULL) {
		TheFirewallHelper = createFirewallHelper();
	}
	if (TheFirewallHelper->detectFirewall() == TRUE) {
		// don't need to detect firewall, already been done.
		delete TheFirewallHelper;
		TheFirewallHelper = NULL;
	}
	/*

	if (TheGameSpyChat && TheGameSpyChat->isConnected())
	{
		const char *keys[3] = { "locale", "wins", "losses" };
		char valueStrings[3][20];
		char *values[3] = { valueStrings[0], valueStrings[1], valueStrings[2] };
		_snprintf(values[0], 20, "%s", TheGameSpyPlayerInfo->getLocale().str());
		_snprintf(values[1], 20, "%d", TheGameSpyPlayerInfo->getWins());
		_snprintf(values[2], 20, "%d", TheGameSpyPlayerInfo->getLosses());
		peerSetGlobalKeys(TheGameSpyChat->getPeer(), 3, (const char **)keys, (const char **)values);
		peerSetGlobalWatchKeys(TheGameSpyChat->getPeer(), GroupRoom,   3, keys, PEERFalse);
		peerSetGlobalWatchKeys(TheGameSpyChat->getPeer(), StagingRoom, 3, keys, PEERFalse);
	}
	*/

//	// animate controls
//	TheShell->registerWithAnimateManager(buttonQuickMatch, WIN_ANIMATION_SLIDE_LEFT, TRUE, 800);
//	TheShell->registerWithAnimateManager(buttonLobby, WIN_ANIMATION_SLIDE_LEFT, TRUE, 600);
//	//TheShell->registerWithAnimateManager(NULL, WIN_ANIMATION_SLIDE_LEFT, TRUE, 400);
//	TheShell->registerWithAnimateManager(buttonBuddies, WIN_ANIMATION_SLIDE_LEFT, TRUE, 200);
//	//TheShell->registerWithAnimateManager(NULL, WIN_ANIMATION_SLIDE_LEFT, TRUE, 1);
//	TheShell->registerWithAnimateManager(buttonBack, WIN_ANIMATION_SLIDE_BOTTOM, TRUE, 1);

	// Show Menu
	((BfmeVirtualHideLayout *)layout)->hide( FALSE );

	// Set Keyboard to Main Parent
	TheWindowManager->winSetFocus( parentWOLWelcome );

	enableControls( ((Rva0050C160GameSpyInfoView *)TheGameSpyInfo)->gotGroupRoomList() );
	TheShell->showShellMap(TRUE);

	updateNumPlayersOnline();
	updateOverallStats();

	UpdateLocalPlayerStats();

	GameSpyMiscPreferences cPref;
	if (cPref.getLocale() < LOC_MIN || cPref.getLocale() > LOC_MAX)
	{
		GameSpyOpenOverlay(GSOVERLAY_LOCALESELECT);
	}

	raiseMessageBoxes = TRUE;
	TheTransitionHandler->setGroup("WOLWelcomeMenuFade");

} // WOLWelcomeMenuInit

} // namespace Rva0050C160Twin
