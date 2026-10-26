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


// FILE: W3DListBox.cpp ///////////////////////////////////////////////////////
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
// File name: W3DListBox.cpp
//
// Created:   Colin Day, June 2001
//
// Desc:      W3D implementation for the list box control
//
//-----------------------------------------------------------------------------
///////////////////////////////////////////////////////////////////////////////

// SYSTEM INCLUDES ////////////////////////////////////////////////////////////
#include <stdlib.h>

#include "../../../../../../../inputs/reference/shims/w3ddisplaystring/GameClient/DisplayString.h"

// USER INCLUDES //////////////////////////////////////////////////////////////
#include "GameClient/GameWindowGlobal.h"
#include "GameClient/GameWindowManager.h"
#include "GameClient/GadgetListBox.h"
#include "W3DDevice/GameClient/W3DGadget.h"
#include "W3DDevice/GameClient/W3DDisplay.h"

// DEFINES ////////////////////////////////////////////////////////////////////

// PRIVATE TYPES //////////////////////////////////////////////////////////////

// PRIVATE DATA ///////////////////////////////////////////////////////////////

// PUBLIC DATA ////////////////////////////////////////////////////////////////

// PRIVATE PROTOTYPES /////////////////////////////////////////////////////////

class DisplayStringSlots
{
public:
	virtual void unused00();
	virtual void unused01();
	virtual void unused02();
	virtual Int getTextLength();
	virtual void unused04();
	virtual void unused05();
	virtual void setFont(GameFont *font);
	virtual GameFont *getFont();
	virtual void setWordWrap(Int wordWrap);
	virtual void unused09();
	virtual void setTextColor(Color color, Color border);
	virtual void unused11();
	virtual void unused12();
	virtual void unused13();
	virtual void draw(Int x, Int y, Int color, Int border);
	virtual void getSize(Int *width, Int *height);
	virtual void unused16();
	virtual void unused17();
	virtual void unused18();
	virtual void unused19();
	virtual void setClipRegion(IRegion2D *region);
};

// BFME's list row keeps the row height as a full Int at +4.
struct ListEntryRowLayout
{
	Int listHeight;
	Int height;
	ListEntryCell *cell;
};

// BFME ListboxData: the flag bytes +0x0F..+0x13 and the Int at +0x30 are
// absent from the Zero Hour declaration, which shifts every later field; their
// names stay address-derived (same layout as GadgetListBoxInput.cpp's view).
struct ListboxDataLayout
{
	Short listLength;
	Short columns;
	Int *columnWidthPercentage;
	Bool autoScroll, autoPurge, scrollBar, multiSelect;
	Bool forceSelect, scrollIfAtEnd, audioFeedback, m_byte0f;
	Bool m_byte10, m_byte11, m_byte12, m_byte13;
	Int *columnWidth;
	ListEntryRowLayout *listData;
	GameWindow *upButton, *downButton, *slider;
	Int totalHeight;
	Short endPos, insertPos;
	Int m_at30;
	Int selectPos;
	Int *selections;
	Short displayHeight;
	UnsignedInt doubleClickTime;
	Short displayPos;
};

// One entry of a window's BFME draw-data tables (enabled +0x48, disabled
// +0xB4, hilite +0x120); the selected-item entries are index 1..4.
struct WindowDrawDataLayout
{
	const Image *image;
	Color color;
	Color borderColor;
};

// BFME Display slots +0x88 / +0x90 (the Zero Hour header has them at +0x68 /
// +0x70); witnessed by 0x007921E0 and 0x00792350 on TheDisplay (0x012F1270).
#define DISPLAY_CLIP_SLOTS_UNUSED(n) virtual void unused##n();
class DisplayClipSlots
{
public:
	DISPLAY_CLIP_SLOTS_UNUSED(00) DISPLAY_CLIP_SLOTS_UNUSED(01) DISPLAY_CLIP_SLOTS_UNUSED(02)
	DISPLAY_CLIP_SLOTS_UNUSED(03) DISPLAY_CLIP_SLOTS_UNUSED(04) DISPLAY_CLIP_SLOTS_UNUSED(05)
	DISPLAY_CLIP_SLOTS_UNUSED(06) DISPLAY_CLIP_SLOTS_UNUSED(07) DISPLAY_CLIP_SLOTS_UNUSED(08)
	DISPLAY_CLIP_SLOTS_UNUSED(09) DISPLAY_CLIP_SLOTS_UNUSED(10) DISPLAY_CLIP_SLOTS_UNUSED(11)
	DISPLAY_CLIP_SLOTS_UNUSED(12) DISPLAY_CLIP_SLOTS_UNUSED(13) DISPLAY_CLIP_SLOTS_UNUSED(14)
	DISPLAY_CLIP_SLOTS_UNUSED(15) DISPLAY_CLIP_SLOTS_UNUSED(16) DISPLAY_CLIP_SLOTS_UNUSED(17)
	DISPLAY_CLIP_SLOTS_UNUSED(18) DISPLAY_CLIP_SLOTS_UNUSED(19) DISPLAY_CLIP_SLOTS_UNUSED(20)
	DISPLAY_CLIP_SLOTS_UNUSED(21) DISPLAY_CLIP_SLOTS_UNUSED(22) DISPLAY_CLIP_SLOTS_UNUSED(23)
	DISPLAY_CLIP_SLOTS_UNUSED(24) DISPLAY_CLIP_SLOTS_UNUSED(25) DISPLAY_CLIP_SLOTS_UNUSED(26)
	DISPLAY_CLIP_SLOTS_UNUSED(27) DISPLAY_CLIP_SLOTS_UNUSED(28) DISPLAY_CLIP_SLOTS_UNUSED(29)
	DISPLAY_CLIP_SLOTS_UNUSED(30) DISPLAY_CLIP_SLOTS_UNUSED(31) DISPLAY_CLIP_SLOTS_UNUSED(32)
	DISPLAY_CLIP_SLOTS_UNUSED(33)
	virtual void setClipRegion( IRegion2D *region );
	DISPLAY_CLIP_SLOTS_UNUSED(35)
	virtual void enableClipping( Bool onoff );
};
#undef DISPLAY_CLIP_SLOTS_UNUSED

inline DisplayClipSlots *displayClipSlots()
{
	return (DisplayClipSlots *)TheDisplay;
}

inline const WindowDrawDataLayout *windowEnabledDrawData(GameWindow *window, Int index)
{
	return (const WindowDrawDataLayout *)((const char *)window + 0x48) + index;
}

inline const WindowDrawDataLayout *windowDisabledDrawData(GameWindow *window, Int index)
{
	return (const WindowDrawDataLayout *)((const char *)window + 0xb4) + index;
}

inline const WindowDrawDataLayout *windowHiliteDrawData(GameWindow *window, Int index)
{
	return (const WindowDrawDataLayout *)((const char *)window + 0x120) + index;
}

inline const Image *bfmeListEnabledImage(GameWindow *window)
{
	return *(const Image **)((const char *)window + 0x48);
}

inline const Image *bfmeListDisabledImage(GameWindow *window)
{
	return *(const Image **)((const char *)window + 0xb4);
}

inline const Image *bfmeListHiliteImage(GameWindow *window)
{
	return *(const Image **)((const char *)window + 0x120);
}

inline Color bfmeListEnabledColor(GameWindow *window)
{
	return *(const Color *)((const char *)window + 0x4c);
}

inline Color bfmeListEnabledBorderColor(GameWindow *window)
{
	return *(const Color *)((const char *)window + 0x50);
}

inline Color bfmeListDisabledColor(GameWindow *window)
{
	return *(const Color *)((const char *)window + 0xb8);
}

inline Color bfmeListDisabledBorderColor(GameWindow *window)
{
	return *(const Color *)((const char *)window + 0xbc);
}

inline Color bfmeListHiliteColor(GameWindow *window)
{
	return *(const Color *)((const char *)window + 0x124);
}

inline Color bfmeListHiliteBorderColor(GameWindow *window)
{
	return *(const Color *)((const char *)window + 0x128);
}

// Keep the existing inline helper rows emitted while this body reads BFME's shifted data.
static const Image *(*s_bfmeKeepListDisabledImage)(GameWindow *) = GadgetListBoxGetDisabledImage;
static const Image *(*s_bfmeKeepListHiliteImage)(GameWindow *) = GadgetListBoxGetHiliteImage;
// drawListBoxText reads the selected-item tables at BFME's offsets, so these
// header helpers it used to inline are kept emitted the same way.
static const Image *(*s_bfmeKeepListSelectedImages[])(GameWindow *) =
{
	GadgetListBoxGetDisabledSelectedItemImageLeft,
	GadgetListBoxGetDisabledSelectedItemImageRight,
	GadgetListBoxGetDisabledSelectedItemImageCenter,
	GadgetListBoxGetDisabledSelectedItemImageSmallCenter,
	GadgetListBoxGetHiliteSelectedItemImageLeft,
	GadgetListBoxGetHiliteSelectedItemImageRight,
	GadgetListBoxGetHiliteSelectedItemImageCenter,
	GadgetListBoxGetHiliteSelectedItemImageSmallCenter,
	GadgetListBoxGetEnabledSelectedItemImageSmallCenter,
};
static Color (*s_bfmeKeepListSelectedColors[])(GameWindow *) =
{
	GadgetListBoxGetDisabledSelectedItemColor,
	GadgetListBoxGetDisabledSelectedItemBorderColor,
	GadgetListBoxGetHiliteSelectedItemColor,
	GadgetListBoxGetHiliteSelectedItemBorderColor,
	GadgetListBoxGetEnabledSelectedItemColor,
};

///////////////////////////////////////////////////////////////////////////////
// PRIVATE FUNCTIONS //////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

// BFME's ICoord2D declares an empty default constructor (W3DGadgetTextEntryDraw.cpp
// and W3DStaticTextDraw_Thunk.cpp match only with it); the shared Zero Hour
// header's POD ICoord2D changes this helper's operand order, so it uses this
// stand-in for its points.
struct ICoord2DWithCtor
{
	ICoord2DWithCtor() {}
	Int x;
	Int y;
};

// Rva007921E0 ================================================================
/** Draw image for the hilite bar.  Retail 0x007921E0 (293 bytes) is Zero
  * Hour's drawHiliteBar without the smallCenter argument; its only caller is
  * drawListBoxText below, which reaches it with a direct call and the
  * compiler-private convention of a file-static, so the name stays
  * address-derived. */
//=============================================================================
static void Rva007921E0( const Image *left, const Image *right,
												 const Image *center,
												 Int startX, Int startY,
												 Int endX, Int endY )
{
	ICoord2DWithCtor barWindowSize;  // end point of bar from window origin
	Int xOffset = 0, yOffset = 0;  // incase we want this functionality later
	ICoord2DWithCtor start, end;
	Int i;
	IRegion2D clipRegion;

	barWindowSize.x = endX - startX;
	barWindowSize.y = endY - startY;

	//
	// the bar window size will always be at least big enough to accomodate
	// the left and right ends
	//
	if( barWindowSize.x < left->getImageWidth() + right->getImageWidth() )
		barWindowSize.x = left->getImageWidth() + right->getImageWidth();

	// get image sizes for the ends
	ICoord2DWithCtor leftSize, rightSize;
	leftSize.x = left->getImageWidth();
	leftSize.y = left->getImageHeight();
	rightSize.x = right->getImageWidth();
	rightSize.y = right->getImageHeight();

	// get two key points used in the end drawing
	ICoord2DWithCtor leftEnd, rightStart;
	leftEnd.x = startX + leftSize.x + xOffset;
	leftEnd.y = startY + barWindowSize.y + yOffset;
	rightStart.x = startX + barWindowSize.x - rightSize.x + xOffset;
	rightStart.y = startY + yOffset;

	// draw the center repeating bar
	Int centerWidth, pieces;

	// get width we have to draw our repeating center in
	centerWidth = rightStart.x - leftEnd.x;

	// how many whole repeating pieces will fit in that width
	pieces = centerWidth / center->getImageWidth();

	// draw the pieces
	start.x = leftEnd.x;
	start.y = startY + yOffset;
	end.y = start.y + barWindowSize.y;
	for( i = 0; i < pieces; i++ )
	{

		end.x = start.x + center->getImageWidth();
		TheWindowManager->winDrawImage( center,
																		start.x, start.y,
																		end.x, end.y );
		start.x += center->getImageWidth();

	}  // end for i

	// clip the remainder of the centre run
	clipRegion.lo.x = leftEnd.x;
	clipRegion.lo.y = startY + yOffset;
	clipRegion.hi.x = leftEnd.x + centerWidth;
	clipRegion.hi.y = start.y + barWindowSize.y;
	displayClipSlots()->setClipRegion( &clipRegion );
	displayClipSlots()->enableClipping( FALSE );

	// draw left end
	start.x = startX + xOffset;
	start.y = startY + yOffset;
	end = leftEnd;
	TheWindowManager->winDrawImage(left, start.x, start.y, end.x, end.y);

	// draw right end
	start = rightStart;
	end.x = start.x + ((Int *)&rightSize)[0];
	end.y = start.y + barWindowSize.y;
	TheWindowManager->winDrawImage(right, start.x, start.y, end.x, end.y);

}  // end Rva007921E0

// drawListBoxText ============================================================
/** Draw the text for a listbox.  Retail 0x00792350 (1388 bytes) is Zero
  * Hour's body on BFME's list layout: single-select can follow the Int at
  * +0x30, flag +0x10 suppresses the selection bar, a missing hilite-bar piece
  * falls back to the centre image, text cells set their colours and centre
  * vertically in the row, and image cells draw only inside an open clip. */
//=============================================================================
static void drawListBoxText( GameWindow *window, WinInstanceData *instData,
													 Int x, Int y, Int width, Int height,
													 Bool useImages )
{
	Int drawY;
	ListboxDataLayout *list = (ListboxDataLayout *)window->winGetUserData();
	Int i;
	Bool selected;
	Int listLineHeight;
	Color textColor;
	IRegion2D clipRegion;
	ICoord2D start, end;

	// set the text clip region to the outline of the listbox
	clipRegion.lo.x = x + 1;
	clipRegion.lo.y = y -3;
	clipRegion.hi.x = x + width - 1;
	clipRegion.hi.y = y + height - 1;

	drawY = y - list->displayPos;

	for( i = 0; ; i++ )
	{

		if( i > 0 )
			if( list->listData[(i - 1)].listHeight >
					(list->displayPos + list->displayHeight) )
				break;

		if( i == list->endPos )
			break;

		if( list->listData[i].listHeight < list->displayPos )
		{
			drawY += (list->listData[i].height + 1);
			continue;
		}

		listLineHeight = list->listData[i].height + 1;
		selected = FALSE;

		if( list->multiSelect )
		{
			Int j = 0;

			while( list->selections[j] >= 0 )
			{
				if( i == list->selections[j] )
				{
					selected = TRUE;
					break;
				}

				j++;
			}
		}
		else
		{
			if( list->m_byte12 && list->m_byte13 )
			{
				if( i == list->m_at30 )
					selected = TRUE;
			}
			else if( i == list->selectPos )
				selected = TRUE;
		}

		// this item is selected, draw the selection color or image
		if( selected && !list->m_byte10 )
		{

			if( useImages )
			{
				const Image *left, *right, *center, *smallCenter;

				if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
				{

					left				= windowDisabledDrawData( window, 1 )->image;
					right				= windowDisabledDrawData( window, 2 )->image;
					center			= windowDisabledDrawData( window, 3 )->image;
					smallCenter = windowDisabledDrawData( window, 4 )->image;

				}  // end if
				else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
				{

					left				= windowHiliteDrawData( window, 1 )->image;
					right				= windowHiliteDrawData( window, 2 )->image;
					center			= windowHiliteDrawData( window, 3 )->image;
					smallCenter = windowHiliteDrawData( window, 4 )->image;

				}  // end else if
				else
				{

					left				= windowEnabledDrawData( window, 1 )->image;
					right				= windowEnabledDrawData( window, 2 )->image;
					center			= windowEnabledDrawData( window, 3 )->image;
					smallCenter = windowEnabledDrawData( window, 4 )->image;

				}  // end else

				// draw select image across area

				//
				// where are we going to draw ... taking into account the clipping
				// region of the edge of the listbox
				//
				start.x = x;
				start.y = drawY;
				end.x = start.x + width;
				end.y = start.y + listLineHeight;

				if( end.y > clipRegion.hi.y )
					end.y = clipRegion.hi.y;
				if( start.y < clipRegion.lo.y )
					start.y = clipRegion.lo.y;

				if( left && right && center && smallCenter )
					Rva007921E0( left, right, center, start.x + 1, start.y, end.x , end.y );
				else if( center )
					TheWindowManager->winDrawImage( center, start.x + 1, start.y, end.x, end.y );

			}  // end if, use images
			else
			{
				Color selectColor = WIN_COLOR_UNDEFINED,
							selectBorder = WIN_COLOR_UNDEFINED;

				if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
				{
					selectColor  = windowDisabledDrawData( window, 1 )->color;
					selectBorder = windowDisabledDrawData( window, 1 )->borderColor;
				}  // end if, disabled
				else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
				{
					selectColor  = windowHiliteDrawData( window, 1 )->color;
					selectBorder = windowHiliteDrawData( window, 1 )->borderColor;
				}  // end else if, hilited
				else
				{
					selectColor  = windowEnabledDrawData( window, 1 )->color;
					selectBorder = windowEnabledDrawData( window, 1 )->borderColor;
				}  // end else, enabled

				// draw border

				//
				// where are we going to draw ... taking into account the clipping
				// region of the edge of the listbox
				//
				start.x = x;
				start.y = drawY;
				end.x = start.x + width;
				end.y = start.y + listLineHeight;

				if( end.y > clipRegion.hi.y )
					end.y = clipRegion.hi.y;
				if( start.y < clipRegion.lo.y )
					start.y = clipRegion.lo.y;

				if( selectBorder != WIN_COLOR_UNDEFINED )
					TheWindowManager->winOpenRect( selectBorder,
																				 WIN_DRAW_LINE_WIDTH,
																				 start.x, start.y,
																				 end.x, end.y );

				// draw filled inner rect

				//
				// where are we going to draw ... taking into account the clipping
				// region of the edge of the listbox
				//
				start.x = x + 1;
				start.y = drawY + 1;
				end.x = start.x + width - 2;
				end.y = start.y + listLineHeight - 2;

				if( end.y > clipRegion.hi.y )
					end.y = clipRegion.hi.y;
				if( start.y < clipRegion.lo.y )
					start.y = clipRegion.lo.y;

				if( selectColor != WIN_COLOR_UNDEFINED )
					TheWindowManager->winFillRect( selectColor,
																				 WIN_DRAW_LINE_WIDTH,
																				 start.x, start.y,
																				 end.x, end.y );

			}  // end else, draw selection with colors

		}  // end if

		Color dropColor = TheWindowManager->winMakeColor( 0, 0, 0, 255 );
		DisplayStringSlots *string;

		ListEntryCell *cells = list->listData[i].cell;
		Int columnX = x;
		IRegion2D columnRegion;
		if( cells )
		{
			// loop through all the cells
			for( Int j = 0; j < list->columns; j++ )
			{
				// setup the Clip Region size

				columnRegion.lo.x = columnX;
				columnRegion.lo.y = drawY;
				if(list->columns == 1 && list->slider && list->slider->winIsHidden())
					columnRegion.hi.x = columnX + width-3;
				else
					columnRegion.hi.x = columnX + list->columnWidth[j];
				columnRegion.hi.y = drawY + list->listData[i].height;
				if(columnRegion.lo.y < clipRegion.lo.y )
					columnRegion.lo.y = clipRegion.lo.y;
				if( columnRegion.hi.y > clipRegion.hi.y )
					columnRegion.hi.y = clipRegion.hi.y;

				// Display the Text Case;
				if(cells[j].cellType == LISTBOX_TEXT)
				{
					textColor = cells[j].color;
					string = (DisplayStringSlots *)cells[j].data;
					if( BitTest( window->winGetStatus(), WIN_STATUS_ONE_LINE ) == TRUE )
						string->setWordWrap(0);

					// make sure the font of the text is the same as the windows
					if( string->getFont() != window->winGetFont() )
						string->setFont( window->winGetFont() );

					// set clip region and colours, then centre the text in the row
					string->setClipRegion( &columnRegion );
					string->setTextColor( textColor, dropColor );
					Int textWidth, textHeight;
					string->getSize( &textWidth, &textHeight );
					Int offsetY = max( 0, (list->listData[i].height - textHeight + 1) / 2 );
					string->draw( columnX + TEXT_X_OFFSET, drawY + offsetY, 1, 1 );
				}// if
				else if(cells[j].cellType == LISTBOX_IMAGE && cells[j].data)
				{
					Int width, height;
					if (cells[j].width > 0)
						width = cells[j].width;
					else
						width = list->columnWidth[j];
					if(cells[j].height > 0)
						height = cells[j].height;
					else
						height = list->listData[i].height;
					if(j == 0)
						width--;
					Int offsetX,offsetY;
					if(width < list->columnWidth[j])
						offsetX = columnX + ((list->columnWidth[j] - width) / 2);
					else
						offsetX = columnX;
					if(height < list->listData[i].height)
						offsetY = drawY + ((list->listData[i].height - height) / 2);
					else
						offsetY = drawY;

					if(offsetX <x+1)
						offsetX = x+1;
					displayClipSlots()->setClipRegion( &columnRegion );
					if( columnRegion.lo.y < columnRegion.hi.y )
						TheWindowManager->winDrawImage( (const Image *)cells[j].data,
																	offsetX, offsetY,
																	offsetX + width, offsetY + height,cells[j].color );

				}//else
				columnX = columnX + list->columnWidth[j];
			}// for
		}//if


		drawY += listLineHeight;
		displayClipSlots()->enableClipping(FALSE);
	}

}  // end drawListBoxText

///////////////////////////////////////////////////////////////////////////////
// PUBLIC FUNCTIONS ///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

// W3DGadgetListBoxDraw =======================================================
/** Draw colored list box using standard graphics */
//=============================================================================
void W3DGadgetListBoxDraw( GameWindow *window, WinInstanceData *instData )
{
	Int width, height, fontHeight, x, y;
	Color background, border, titleColor, titleBorder;
	ListboxDataLayout *list = (ListboxDataLayout *)window->winGetUserData();
	ICoord2D size;
	DisplayStringSlots *title = (DisplayStringSlots *)instData->getTextDisplayString();

	// get window position and size
	window->winGetScreenPosition( &x, &y );
	window->winGetSize( &size.x, &size.y );

	// get font height
	fontHeight = TheWindowManager->winFontHeight( instData->getFont() );

	// alias width and height from size
	width = size.x;
	height = size.y;

	// get the right colors
	if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
	{
		background		= bfmeListDisabledColor( window );
		border				= bfmeListDisabledBorderColor( window );
		titleColor		= window->winGetDisabledTextColor();
		titleBorder		= window->winGetDisabledTextBorderColor();
	}  // end if, disabled
	else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
	{
		background		= bfmeListHiliteColor( window );
		border				= bfmeListHiliteBorderColor( window );
		titleColor		= window->winGetHiliteTextColor();
		titleBorder		= window->winGetHiliteTextBorderColor();
	}  // end else if, hilited
	else
	{
		background		= bfmeListEnabledColor( window );
		border				= bfmeListEnabledBorderColor( window );
		titleColor		= window->winGetEnabledTextColor();
		titleBorder		= window->winGetEnabledTextBorderColor();
	}  // end else, enabled

	// Draw the title
	if( title && title->getTextLength() )
	{
	
		// set the font of this text to that of the window if not already
		if( title->getFont() != window->winGetFont() )
			title->setFont( window->winGetFont() );
			
		// draw the text
		title->setTextColor( titleColor, titleBorder );
		title->draw( x + 1, y, 1, 1 );

		y += fontHeight + 1;
		height -= fontHeight + 1;

	}  // end if

	// draw the back border
	if( border != WIN_COLOR_UNDEFINED )
		TheWindowManager->winOpenRect( border, WIN_DRAW_LINE_WIDTH,
																	 x, y, x + width, y + height );

	// draw background
	if( background != WIN_COLOR_UNDEFINED )
		TheWindowManager->winFillRect( background, WIN_DRAW_LINE_WIDTH,
																	 x + 1, y + 1, 
																	 x + width - 1, y + height - 1 );

	// If ScrollBar was requested ... adjust width.
	if( list->slider  && !list->slider->winIsHidden())
	{
		ICoord2D sliderSize;

		list->slider->winGetSize( &sliderSize.x, &sliderSize.y );
		width -= (sliderSize.x +3);

	}  // end if

	// draw the text
	drawListBoxText( window, instData, x, y + 4 , width, height-4, TRUE );

	

}  // end W3DGadgetListBoxDraw

// W3DGadgetListBoxImageDraw ==================================================
/** Draw list box with user supplied images */
//=============================================================================
void W3DGadgetListBoxImageDraw( GameWindow *window, WinInstanceData *instData )
{
	Int width, height, x, y;
	const Image *image;
	ListboxDataLayout *list = (ListboxDataLayout *)window->winGetUserData();
	ICoord2D size;
	Color titleColor, titleBorder;
	DisplayStringSlots *title = (DisplayStringSlots *)instData->getTextDisplayString();

	// get window position and size
	window->winGetScreenPosition( &x, &y );
	window->winGetSize( &size.x, &size.y );

	// save off width and height so we can change them
	width = size.x;
	height = size.y;

	// If ScrollBar was requested ... adjust width.
	if( list->slider )
	{
		ICoord2D sliderSize;

		list->slider->winGetSize( &sliderSize.x, &sliderSize.y );
		width -= sliderSize.x;

	}  // end if

	// get the image
	if( BitTest( window->winGetStatus(), WIN_STATUS_ENABLED ) == FALSE )
	{
		image				= bfmeListDisabledImage( window );
		titleColor	= window->winGetDisabledTextColor();
		titleBorder = window->winGetDisabledTextBorderColor();
	}
	else if( BitTest( instData->getState(), WIN_STATE_HILITED ) )
	{
		image				= bfmeListHiliteImage( window );
		titleColor	= window->winGetHiliteTextColor();
		titleBorder = window->winGetHiliteTextBorderColor();
	}
	else
	{
		image				= bfmeListEnabledImage( window );
		titleColor	= window->winGetEnabledTextColor();
		titleBorder = window->winGetEnabledTextBorderColor();
	}

	// draw the back image
	if( image )
	{
		ICoord2D start, end;

		start.x = x + instData->m_imageOffset.x;
		start.y = y + instData->m_imageOffset.y;
		end.x = start.x + width;
		end.y = start.y + height;
		TheWindowManager->winDrawImage( image, 
																		start.x, start.y, 
																		end.x, end.y );

	}  // end if

	// Draw the title
	if( title && title->getTextLength() )
	{

		// set font to font of the window if not already
		if( title->getFont() != window->winGetFont() )
			title->setFont( window->winGetFont() );

		// draw the text
		title->setTextColor( titleColor, titleBorder );
		title->draw( x + 1, y, 1, 1 );

		y += TheWindowManager->winFontHeight( instData->getFont() );
		height -= TheWindowManager->winFontHeight( instData->getFont() ) + 1;

	}  // end if

	// draw the listbox text
	drawListBoxText( window, instData, x, y+4, width, height-4, TRUE );

	

}  // end W3DGadgetListBoxImageDraw
