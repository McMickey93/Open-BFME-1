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

// FILE: W3DGameFont.cpp //////////////////////////////////////////////////////
//-----------------------------------------------------------------------------
//                                                                          
//                       Westwood Studios Pacific.                          
//                                                                          
//                       Confidential Information                           
//                Copyright (C) 2001 - All Rights Reserved                  
//                                                                          
//-----------------------------------------------------------------------------
//
// Project:    RTS3
//
// File name:  W3DGameFont.cpp
//
// Created:    Colin Day, June 2001
//
// Desc:       W3D implementation for managing font definitions
//
//-----------------------------------------------------------------------------
///////////////////////////////////////////////////////////////////////////////

// SYSTEM INCLUDES ////////////////////////////////////////////////////////////
#include <stdlib.h>

// USER INCLUDES //////////////////////////////////////////////////////////////
#include "Common/Debug.h"
#include "W3DDevice/GameClient/W3DGameFont.h"
#include "WW3D2/WW3D.h"
#include "WW3D2/AssetMgr.h"
#include "WW3D2/Render2DSentence.h"
#include "GameClient/GlobalLanguage.h"

// DEFINES ////////////////////////////////////////////////////////////////////

// PRIVATE TYPES //////////////////////////////////////////////////////////////

// PRIVATE DATA ///////////////////////////////////////////////////////////////

// PUBLIC DATA ////////////////////////////////////////////////////////////////

// PRIVATE PROTOTYPES /////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
// PRIVATE FUNCTIONS //////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

// BFME's float-size/four-key loader is owned by W3DFontLibraryLoadFontDataBFME.cpp.

// W3DFontLibrary::releaseFontData ============================================
/** Release font data */
//=============================================================================
void W3DFontLibrary::releaseFontData( GameFont *font )
{
	// Retain this TU's ledger-owned accessor after removing the Zero Hour loader.
	(void)&FontCharsClass::Get_Char_Height;

	// presently we don't need to do anything because fonts are handled in
	// the W3D asset manager which is all taken for of us
	if (font && font->fontData)
	{
		if(((FontCharsClass *)(font->fontData))->AlternateUnicodeFont)
			((FontCharsClass *)(font->fontData))->AlternateUnicodeFont->Release_Ref();
		((FontCharsClass *)(font->fontData))->Release_Ref();
	}
	font->fontData = NULL;
	
}  // end releaseFont

// PUBLIC FUNCTIONS ///////////////////////////////////////////////////////////

