#include "../../../Libraries/Source/WWVegas/WWLib/string_base.h"

// DisplayString::removeLastChar, retail 0x0040FF90 (19 bytes): Zero Hour's
// body, with notifyTextChanged at BFME's vtable slot +0x10 (the shared
// DisplayString.h still has Zero Hour's +0x14). Open-BFME-2's matched
// removeLastChar is byte-identical and BFME1's ILT slot confirms the name.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameClient/DisplayString.h
class DisplayString
{
public:
	virtual void slot00();
	virtual void slot04();
	virtual void slot08();
	virtual void slot0C();
	virtual void notifyTextChanged();	// +0x10
	virtual void removeLastChar();

protected:
	StringBase<unsigned short> m_textString;	// +0x04
};

void DisplayString::removeLastChar()
{
	m_textString.removeLastChar();
	notifyTextChanged();
}
