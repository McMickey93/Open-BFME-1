// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main
// stlport
#define Matrix4x4 Matrix4  // BFME renamed it
#define __PLACEMENT_VEC_NEW_INLINE  // always.h/GameMemory.h define array placement-new themselves
// stlport
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

// FILE: ChallengeGenerals.h //////////////////////////////////////////////////////////////////////
// Author: Steve Copeland, 6/24/2003
// Desc:   This is a manager for data pertaining to the Generals' Challenge personas and related GUI.
///////////////////////////////////////////////////////////////////////////////////////////////////

#include "PreRTS.h"	// This must go first in EVERY cpp file int the GameEngine

#include "GameClient/ChallengeGenerals.h"

#ifdef _INTERNAL
// for occasional debugging...
//#pragma optimize("", off)
//#pragma MESSAGE("************************************** WARNING, optimization disabled for debugging purposes")
#endif

ChallengeGenerals *TheChallengeGenerals = NULL;

ChallengeGenerals *createChallengeGenerals( void )
{
	return MSGNEW("ChallengeGenerals") ChallengeGenerals;
}


// ??0ChallengeGenerals@@ present-unmatched
ChallengeGenerals::ChallengeGenerals()
{
	//ctor
}


// ??1ChallengeGenerals@@ present-unmatched
ChallengeGenerals::~ChallengeGenerals()
{
	//dtor
}


// ?init@ChallengeGenerals@@ present-unmatched
void ChallengeGenerals::init( void )
{
	INI ini;
	ini.load( AsciiString( "Data\\INI\\ChallengeMode.ini" ), INI_LOAD_OVERWRITE, NULL );
}


extern "C" const FieldParse __identifier("?m_creditsFieldParseTable@CreditsManager@@2QBUFieldParse@@B")[];


//-------------------------------------------------------------------------------------------------
/** Parse Gen Challenge entries */
//-------------------------------------------------------------------------------------------------
void INI::parseChallengeModeDefinition( INI* ini )
{
	if( TheChallengeGenerals )
	{
		ini->initFromINI( TheChallengeGenerals, __identifier("?m_creditsFieldParseTable@CreditsManager@@2QBUFieldParse@@B") );
	}
}

// ?getPlayerGeneralByCampaignName@ChallengeGenerals@@ present-unmatched
const GeneralPersona* ChallengeGenerals::getPlayerGeneralByCampaignName( AsciiString name ) const 
{
	for (Int i = 0; i < NUM_GENERALS; i++)
	{
		AsciiString campaignName = m_position[i].getCampaign();
		if (campaignName.compareNoCase( name.str() ) == 0)
			return &m_position[i];
	}
	DEBUG_ASSERTCRASH(NULL, ("Can't find General by Campaign Name"));
	return NULL;
}

// ?getGeneralByGeneralName@ChallengeGenerals@@ present-unmatched
const GeneralPersona* ChallengeGenerals::getGeneralByGeneralName( AsciiString name ) const
{
	for (Int i = 0; i < NUM_GENERALS; i++)
	{
		AsciiString generalName = m_position[i].getBioName();
		if (generalName.compareNoCase( name.str() ) == 0)
			return &m_position[i];
	}
	return NULL;
}

// ?getGeneralByTemplateName@ChallengeGenerals@@ present-unmatched
const GeneralPersona* ChallengeGenerals::getGeneralByTemplateName( AsciiString name ) const
{
	for (Int i = 0; i < NUM_GENERALS; i++)
	{
		AsciiString templateName = m_position[i].getPlayerTemplateName();
		if (templateName.compareNoCase( name.str() ) == 0)
			return &m_position[i];
	}
	return NULL;
}
