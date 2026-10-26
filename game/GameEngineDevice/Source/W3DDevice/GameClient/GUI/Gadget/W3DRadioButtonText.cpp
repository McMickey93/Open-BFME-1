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

// FILE: W3DRadioButton.cpp ///////////////////////////////////////////////////
//-----------------------------------------------------------------------------
//                                                                          
//                       Westwood Studios Pacific.                          
//                                                                          
//                       Confidential Information                           
//                Copyright (C) 2001 - All Rights Reserved                  
//                                                                          
//-----------------------------------------------------------------------------
//
// Project:   RTS3
//
// File name: W3DRadioButtonText.cpp
//
// Created:   Colin Day, June 2001
//
// Desc:      W3D methods needed to implement the RadioButton UI control
//
//-----------------------------------------------------------------------------
///////////////////////////////////////////////////////////////////////////////

// SYSTEM INCLUDES ////////////////////////////////////////////////////////////
#include <stdlib.h>

// USER INCLUDES //////////////////////////////////////////////////////////////
#include "GameClient/GameWindowGlobal.h"
#include "GameClient/GameWindowManager.h"
#include "GameClient/GadgetRadioButton.h"
#include "W3DDevice/GameClient/W3DGadget.h"
#include "W3DDevice/GameClient/W3DDisplay.h"

// DEFINES ////////////////////////////////////////////////////////////////////

// PRIVATE TYPES //////////////////////////////////////////////////////////////

// PRIVATE DATA ///////////////////////////////////////////////////////////////

// PUBLIC DATA ////////////////////////////////////////////////////////////////

// PRIVATE PROTOTYPES /////////////////////////////////////////////////////////

// BFME's DisplayString interface predates the Zero Hour header used to build
// this pristine TU: it has no virtual destructor slot and carries a separate
// text-color setter.  Keep that ABI difference local to the one BFME body.
class BFMEDisplayString
{
public:
	virtual void unused00();
	virtual void unused01();
	virtual void unused02();
	virtual Int getTextLength();
	virtual void unused04();
	virtual void unused05();
	virtual void setFont( GameFont *font );
	virtual GameFont *getFont();
	virtual void unused08();
	virtual void unused09();
	virtual void setTextColor( Color color, Color dropColor );
	virtual void unused11();
	virtual void unused12();
	virtual void unused13();
	virtual void draw( Int x, Int y, Int xDrop, Int yDrop );
	virtual void getSize( Int *width, Int *height );
};

// drawRadioButtonText ========================================================
/** Draw the text for a RadioButton.
 *  Retail 0x00796310 (289 B) is this same-TU static, so VC7.1 passes its two
 *  parameters in registers: window arrives in ECX (it becomes the `this` of
 *  every GameWindow accessor call) and instData in EAX (+0x05 mov ebx,eax then
 *  +0x07 mov esi,[ebx+0x19c] = WinInstanceData::m_text); the caller at
 *  0x00796480+0x1f8 loads them the same way. An earlier note stated the
 *  opposite assignment; the disassembly above is the correct one. That
 *  convention only reproduces beside in-TU callers, which is why the two draw
 *  callbacks below restate Gadget/W3DRadioButton.cpp's definitions. The color
 *  callback at 0x00796480 is now verified; the image callback at 0x00796710
 *  remains the pre-existing unclaimed companion. */
//=============================================================================
static void drawRadioButtonText( GameWindow *window, WinInstanceData *instData )
{
	ICoord2D origin, size, textPos;
	ICoord2D textSize;
	Color textColor, dropColor;
	DisplayString *text = instData->getTextDisplayString();
	BFMEDisplayString *bfmeText = (BFMEDisplayString *)text;

	// sanity
	if( text == NULL || bfmeText->getTextLength() == 0 )
		return;

	// get window position and size
	window->winGetScreenPosition( &origin.x, &origin.y );
	window->winGetSize( &size.x, &size.y );

	// get the right text color
	if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
	{
		textColor = window->winGetDisabledTextColor();
		dropColor = window->winGetDisabledTextBorderColor();
	}  // end if, disabled
	else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
	{
		textColor = window->winGetHiliteTextColor();
		dropColor = window->winGetHiliteTextBorderColor();
	}  // end else if, hilited
	else
	{
		textColor = window->winGetEnabledTextColor();
		dropColor = window->winGetEnabledTextBorderColor();
	}  // end enabled only

	// set our font to that of our parent if not the same
	if( bfmeText->getFont() != window->winGetFont() )
		bfmeText->setFont( window->winGetFont() );

	// get text size
	bfmeText->getSize( &textSize.x, &textSize.y );

	// set the location for our text
	textPos.x = origin.x + (size.x / 2) - (textSize.x / 2);
	textPos.y = origin.y + (size.y / 2) - (textSize.y / 2);

	// draw it
	bfmeText->setTextColor( textColor, dropColor );
	bfmeText->draw( textPos.x, textPos.y, 1, 1 );

}  // end drawRadioButtonText

// PRIVATE FUNCTIONS //////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
// PUBLIC FUNCTIONS ///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

// W3DGadgetRadioButtonDraw ===================================================
/** Draw colored check box using standard graphics */
//=============================================================================
// Keep the canonical coordinate layout, with a local construction boundary.
// An empty default constructor preserves retail SIB and stack allocation.
// Evidence: targets/game/reverse/identity_evidence/00796480-radio-draw.md.
template <class Coord>
struct DefaultConstructed00796480 : Coord
{
	DefaultConstructed00796480() {}
};
// Reuse WinInstanceData's m_text layout and the BFME virtual-slot view above.
struct Rva00796480InstanceData : WinInstanceData
{
	Int getTextLength()
	{
		return m_text ? ((BFMEDisplayString *)m_text)->getTextLength() : 0;
	}
};
void W3DGadgetRadioButtonDraw( GameWindow *window, WinInstanceData *instData )
{
	Int checkOffsetFromLeft;
	Color backColor,
				backBorder,
				boxColor,
				boxBorder;
	DefaultConstructed00796480<ICoord2D> origin, size, start, end;
	// Only the inline color getters use this view: BFME's three draw arrays
	// start four bytes later than the Zero Hour header used by this TU.
	GameWindow *colorWindow = (GameWindow *)((char *)window + 4);

	// get window position and size
	window->winGetScreenPosition( &origin.x, &origin.y );
	window->winGetSize( &size.x, &size.y );

	// compute start of check offset
	checkOffsetFromLeft = size.x / 16;

	//
	// get the colors we should be using to draw, see GadgetRadioButton.h
	// draw appropriate state, see GadgetRadioButton.h for info
	//
	if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
	{

		// disabled background
		backColor			= GadgetRadioGetDisabledColor( colorWindow );
		backBorder		= GadgetRadioGetDisabledBorderColor( colorWindow );

		// check box
		if( BitTest( instData->getState(), WIN_STATE_SELECTED ) )
		{
				boxColor		= GadgetRadioGetDisabledCheckedBoxColor( colorWindow );
				boxBorder		= GadgetRadioGetDisabledCheckedBoxBorderColor( colorWindow );
		}
		else
		{
				boxColor		= GadgetRadioGetDisabledUncheckedBoxColor( colorWindow );
				boxBorder		= GadgetRadioGetDisabledUncheckedBoxBorderColor( colorWindow );
		}

	}  // end if
	else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
	{

		// hilited background 
		backColor			= GadgetRadioGetHiliteColor( colorWindow );
		backBorder		= GadgetRadioGetHiliteBorderColor( colorWindow );

		// check box
		if( BitTest( instData->getState(), WIN_STATE_SELECTED ) )
		{
			boxColor		= GadgetRadioGetHiliteCheckedBoxColor( colorWindow );
			boxBorder		= GadgetRadioGetHiliteCheckedBoxBorderColor( colorWindow );
		}
		else
		{
			boxColor		= GadgetRadioGetHiliteUncheckedBoxColor( colorWindow );
			boxBorder		= GadgetRadioGetHiliteUncheckedBoxBorderColor( colorWindow );
		}

	}  // end else if
	else
	{

		// enabled background 
		backColor			= GadgetRadioGetEnabledColor( colorWindow );
		backBorder		= GadgetRadioGetEnabledBorderColor( colorWindow );

		// check box
		if( BitTest( instData->getState(), WIN_STATE_SELECTED ) )
		{
			boxColor		= GadgetRadioGetEnabledCheckedBoxColor( colorWindow );
			boxBorder		= GadgetRadioGetEnabledCheckedBoxBorderColor( colorWindow );
		}
		else
		{
			boxColor		= GadgetRadioGetEnabledUncheckedBoxColor( colorWindow );
			boxBorder		= GadgetRadioGetEnabledUncheckedBoxBorderColor( colorWindow );
		}

	}  // end else

	// draw background border
	start.x = origin.x;
	start.y = origin.y;
	end.x = start.x + size.x;
	end.y = start.y + size.y;
	TheWindowManager->winOpenRect( backBorder, WIN_DRAW_LINE_WIDTH, 
																 start.x, start.y, end.x, end.y );

	// draw the background
	start.x++;
	start.y++;
	end.x--;
	end.y--;
	TheWindowManager->winFillRect( backColor, WIN_DRAW_LINE_WIDTH, 
																 start.x, start.y, end.x, end.y );


	
	// draw box border
	start.x = origin.x + size.y;
	start.y = origin.y;
	end.x = start.x;
	end.y = start.y + size.y;
	TheWindowManager->winDrawLine( backBorder, WIN_DRAW_LINE_WIDTH, 
																 start.x, start.y, end.x, end.y );

	// draw box for button
	start.x = origin.x + 1;
	start.y = origin.y + 1;
	end.x	= origin.x + size.y -1;
	end.y = origin.y + size.y -1;
	TheWindowManager->winFillRect( boxColor, WIN_DRAW_LINE_WIDTH, 
																 start.x, start.y, end.x, end.y );

	// draw box border
	start.x = origin.x + size.x - size.y;
	start.y = origin.y;
	end.x = start.x;
	end.y = start.y + size.y;
	TheWindowManager->winDrawLine( backBorder, WIN_DRAW_LINE_WIDTH, 
																 start.x, start.y, end.x, end.y );

	// draw box for button
	start.x = origin.x + size.x - size.y;
	start.y = origin.y + 1;
	end.x	= origin.x + size.x -1;
	end.y = origin.y + size.y -1;
	TheWindowManager->winFillRect( boxColor, WIN_DRAW_LINE_WIDTH, 
																 start.x, start.y, end.x, end.y );
	// draw the button text
	if( ((Rva00796480InstanceData *)instData)->getTextLength() )
		drawRadioButtonText( window, instData );

	

}  // end W3DGadgetRadioButtonDraw


class Rva00796710Display { public:
virtual void slot00();
virtual void slot01();
virtual void slot02();
virtual void slot03();
virtual void slot04();
virtual void slot05();
virtual void slot06();
virtual void slot07();
virtual void slot08();
virtual void slot09();
virtual void slot10();
virtual void slot11();
virtual void slot12();
virtual void slot13();
virtual void slot14();
virtual void slot15();
virtual void slot16();
virtual void slot17();
virtual void slot18();
virtual void slot19();
virtual void slot20();
virtual void slot21();
virtual void slot22();
virtual void slot23();
virtual void slot24();
virtual void slot25();
virtual void slot26();
virtual void slot27();
virtual void slot28();
virtual void slot29();
virtual void slot30();
virtual void slot31();
virtual void slot32();
virtual void slot33();
virtual void setClipRegion(IRegion2D *);
virtual void slot35();
virtual void enableClipping(Bool);
};
// Retail inlines the GameWindow image accessors: each is a load from the
// WinInstanceData embedded at GameWindow+0x30.
class Rva00796710Window { public:
	__forceinline const Image *winGetEnabledImage( Int index ) { return instData()->m_enabledDrawData[ index ].image; }
	__forceinline const Image *winGetDisabledImage( Int index ) { return instData()->m_disabledDrawData[ index ].image; }
	__forceinline const Image *winGetHiliteImage( Int index ) { return instData()->m_hiliteDrawData[ index ].image; }
private:
	__forceinline WinInstanceData *instData( void ) { return reinterpret_cast<WinInstanceData *>( reinterpret_cast<char *>( this ) + 0x30 ); }
};

void W3DGadgetRadioButtonImageDraw( GameWindow *window, 
																	WinInstanceData *instData )
{
	const Image *leftImage, *rightImage, *centerImage;
	DefaultConstructed00796480<ICoord2D> origin, size, start, end;
	Int xOffset, yOffset;
	Int i;

	// get screen position and size
	window->winGetScreenPosition( &origin.x, &origin.y );
	window->winGetSize( &size.x, &size.y );

	IRegion2D clipLeft;

	// get image offset
	xOffset = instData->m_imageOffset.x;
	yOffset = instData->m_imageOffset.y;

	if( BitTest( instData->getState(), WIN_STATE_SELECTED ) )
	{
		//backgroundImage	= GadgetRadioGetEnabledCheckedBoxImage( window );
		leftImage					= ((Rva00796710Window *)window)->winGetHiliteImage( 3 );
		centerImage				= ((Rva00796710Window *)window)->winGetHiliteImage( 4 );
		rightImage				= ((Rva00796710Window *)window)->winGetHiliteImage( 5 );
		
	}
	else if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
	{
		// disabled background
		leftImage					= ((Rva00796710Window *)window)->winGetDisabledImage( 0 );
		centerImage				= ((Rva00796710Window *)window)->winGetDisabledImage( 1 );
		rightImage				= ((Rva00796710Window *)window)->winGetDisabledImage( 2 );
		
	}  // end if
	else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
	{
		// hilited background 
		leftImage					= ((Rva00796710Window *)window)->winGetHiliteImage( 0 );
		centerImage				= ((Rva00796710Window *)window)->winGetHiliteImage( 1 );
		rightImage				= ((Rva00796710Window *)window)->winGetHiliteImage( 2 );
		
	}  // end else if
	else
	{
		// enabled background 
		leftImage					= ((Rva00796710Window *)window)->winGetEnabledImage( 0 );
		centerImage				= ((Rva00796710Window *)window)->winGetEnabledImage( 1 );
		rightImage				= ((Rva00796710Window *)window)->winGetEnabledImage( 2 );
		
	}  // end else

	// sanity, we need to have these images to make it look right
	if( leftImage == NULL || centerImage == NULL || 
			rightImage == NULL )
		return;

	// get image sizes for the ends
	DefaultConstructed00796480<ICoord2D> leftSize, rightSize;
	leftSize.x = leftImage->getImageWidth();
	leftSize.y = leftImage->getImageHeight();
	rightSize.x = rightImage->getImageWidth();
	rightSize.y = rightImage->getImageHeight();

	// get two key points used in the end drawing
	DefaultConstructed00796480<ICoord2D> leftEnd, rightStart;
	leftEnd.x = origin.x + leftSize.x + xOffset;
	leftEnd.y = origin.y + size.y + yOffset;
	rightStart.x = origin.x + size.x - rightSize.x + xOffset;
	rightStart.y = origin.y  + size.y + yOffset;



	// draw the center repeating bar
	Int centerWidth, pieces;

	// get width we have to draw our repeating center in
	centerWidth = rightStart.x - leftEnd.x;

	// how many whole repeating pieces will fit in that width
	pieces = centerWidth / centerImage->getImageWidth();
	pieces++;
	// draw the pieces
	start.x = leftEnd.x;
	start.y = origin.y + yOffset;
	end.y =origin.y + size.y + yOffset;
	
	clipLeft.lo.x = leftEnd.x;
	clipLeft.lo.y = origin.y;
	clipLeft.hi.y = leftEnd.y;
	clipLeft.hi.x = rightStart.x	;


	((Rva00796710Display *)TheDisplay)->setClipRegion(&clipLeft);
	
	for( i = 0; i < pieces; i++ )
	{
		end.x = start.x + centerImage->getImageWidth();
		TheWindowManager->winDrawImage( centerImage, 
																		start.x, start.y,
																		end.x, end.y );	
		start.x += centerImage->getImageWidth();
	}  // end for i
	
	((Rva00796710Display *)TheDisplay)->enableClipping(FALSE);	
	// draw left end
	start.x = origin.x + xOffset;
	start.y = origin.y + yOffset;
	end = leftEnd;
	TheWindowManager->winDrawImage(leftImage, start.x, start.y, end.x, end.y);
	// draw right end
	start.x = rightStart.x;
	start.y = origin.y + yOffset;
	end.x = origin.x + size.x;
	end.y = leftEnd.y;
	TheWindowManager->winDrawImage(rightImage, start.x, start.y, end.x, end.y);

	// draw the text
	if( ((Rva00796480InstanceData *)instData)->getTextLength() )
		drawRadioButtonText( window, instData );

	
}  // end W3DGadgetHorizontalSliderImageDraw

