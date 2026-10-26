// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/stringbaseascii /Iinputs/reference/shims/displaystring /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Igame/Libraries/Source/WWVegas/WWLib
// stlport
#define Matrix4x4 Matrix4
#define __PLACEMENT_VEC_NEW_INLINE

#define UNICODESTRING_H
#include "unicode_string.h"

// Retail inlines character access and calls the StringBase comparison directly.
template<> inline unsigned short StringBase<unsigned short>::getCharAt(int index) const
{
    return m_data ? m_data->data[index] : 0;
}
inline UnicodeString::UnicodeString() { m_text = 0; }
inline UnicodeString::UnicodeString(const UnicodeString &that)
{
    ((StringBase<unsigned short> *)this)->StringBase<unsigned short>::StringBase(
        *(const StringBase<unsigned short> *)&that);
}

inline bool operator==(const UnicodeString &a, const UnicodeString &b)
{
    return ((const StringBase<unsigned short> &)a).compare(
        (const StringBase<unsigned short> &)b) == 0;
}

#include "PreRTS.h"

#include "GameClient/DisplayString.h"

// Retail inlines ~UnicodeString: temporaries are released by a direct call to
// StringBase<unsigned short>::releaseBuffer (0x008881D0), not the ??1UnicodeString stub.
inline UnicodeString::~UnicodeString() { ((StringBase<unsigned short> *)this)->releaseBuffer(); }

class GameWindow;

typedef struct _EntryData
{
	DisplayString *text;
	DisplayString *sText;
	DisplayString *constructText;
	Bool secretText;
	Bool numericalOnly;
	Bool alphaNumericalOnly;
	Bool aSCIIOnly;
	Short maxTextLen;
	Bool receivedUnichar;
	Bool drawTextFromStart;
	GameWindow *constructList;
	void *bfmeEntryPad;
	UnsignedShort charPos;
	UnsignedShort conCharPos;
} EntryData;

extern Bool shiftDown;
extern Bool altDown;
extern Bool ctrlDown;
extern Bool absolute;
extern UnicodeString alt;
extern UnicodeString ctrl;
extern UnicodeString shift;

void setKeyDown( UnicodeString mod, Bool b );

void doKeyUp( EntryData *e, UnicodeString mod )
{
	char c = ((const StringBase<unsigned short> &)e->text->getText()).getCharAt( e->text->getTextLength() - 1 );
	if( c == '+' )
	{
		if( altDown && ctrlDown && shiftDown )
		{
			if( mod == shift )
			{
				UnicodeString temp = alt;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&ctrl );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
			else if( mod == alt )
			{
				UnicodeString temp = ctrl;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&shift );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
			else if( mod == ctrl )
			{
				UnicodeString temp = alt;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&shift );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
		}
		else if( altDown && ctrlDown )
		{
			if( mod == alt )
			{
				e->text->setText( ctrl );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
			else if( mod == ctrl )
			{
				e->text->setText( ctrl );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
		}
		else if( altDown && shiftDown )
		{
			if( mod == alt )
			{
				e->text->setText( shift );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
			else if( mod == shift )
			{
				e->text->setText( alt );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
		}
		else if( ctrlDown && shiftDown )
		{
			if( mod == ctrl )
			{
				e->text->setText( shift );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
			else if( mod == shift )
			{
				e->text->setText( ctrl );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, false );
			}
		}
		else
		{
			e->text->setText( UnicodeString::TheEmptyString );
			e->sText->setText( UnicodeString::TheEmptyString );
			e->charPos = e->text->getTextLength();
			setKeyDown( mod, false );
		}
	}
	else
	{
		absolute = true;
	}
}

void doKeyDown( EntryData *e, UnicodeString mod )
{
	if( e->text->getTextLength() <= 1 )
	{
		e->text->setText( mod );
		e->sText->setText( mod );
		e->charPos = e->text->getTextLength();
		setKeyDown( mod, true );
	}
	else
	{
		char c = ((const StringBase<unsigned short> &)e->text->getText()).getCharAt( e->text->getTextLength() - 1 );
		if( c != '+' && absolute )
		{
			e->text->setText( mod );
			e->sText->setText( mod );
			e->charPos = e->text->getTextLength();
			setKeyDown( shift, false );
			setKeyDown( alt, false );
			setKeyDown( ctrl, false );
			setKeyDown( mod, true );
			absolute = false;
		}
		else
		{
			if( mod == shift && shiftDown )
			{
			}
			else if( mod == ctrl && ctrlDown )
			{
			}
			else if( mod == alt && altDown )
			{
			}
			else if( altDown && ctrlDown )
			{
				UnicodeString temp = alt;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&ctrl );
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&mod );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, true );
			}
			else if( altDown && shiftDown )
			{
				UnicodeString temp = alt;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&ctrl );
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&shift );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, true );
			}
			else if( altDown )
			{
				UnicodeString temp = alt;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&mod );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, true );
			}
			else if( ctrlDown && shiftDown )
			{
				UnicodeString temp = alt;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&ctrl );
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&shift );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, true );
			}
			else if( ctrlDown )
			{
				if( mod == alt )
				{
					UnicodeString temp = mod;
					((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&ctrl );
					e->text->setText( temp );
					e->charPos = e->text->getTextLength();
					setKeyDown( mod, true );
				}
				else
				{
					UnicodeString temp = ctrl;
					((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&mod );
					e->text->setText( temp );
					e->charPos = e->text->getTextLength();
					setKeyDown( mod, true );
				}
			}
			else if( shiftDown )
			{
				UnicodeString temp = mod;
				((StringBase<unsigned short> *)&temp)->concat( *(const StringBase<unsigned short> *)&shift );
				e->text->setText( temp );
				e->charPos = e->text->getTextLength();
				setKeyDown( mod, true );
			}
		}
	}
}
