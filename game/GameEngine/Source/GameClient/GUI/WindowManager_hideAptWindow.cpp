// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/campaignmanagerascii /Iinputs/reference/shims/stringbaseunicode /Igame/Libraries/Source/WWVegas/WWLib
//
// WindowManager::hideAptWindow.  Index is thiscall, slots live at this+0xa8
// with stride 0x14, and a set flag-bit 1 at slot+0x10 is required.  TheMouse
// (0x012F4C5C) gets an empty tooltip first; the UnicodeString by-value
// temporary needs the stringbaseunicode shim so the ctor emits retail's
// `mov [esp+N],esp` / `mov ecx,esp` order.  The inner hide is the already-
// pinned ILT 0x0003F3E1 (?bfmeHide1183@BfmeW1183@@QAEXI@Z).

#include <wchar.h>
#include "Common/UnicodeString.h"

struct RGBColor;

class Mouse
{
public:
	void setCursorTooltip(UnicodeString tooltip, int delay, const RGBColor *color, float width);
};

extern Mouse *TheMouse;

class WindowManager
{
public:
	bool hideAptWindow(int index);

private:
	char m_unmodelled[0xA8];
	struct Slot
	{
		char m_unmodelled_00[0x10];
		unsigned char m_flags;
		char m_pad[3];
	} m_aptWindows[12];
};

// The inner hide is reached through ILT 0x0003F3E1, the ledger's 5-byte row
// ?j_0003f3e1@@YAXXZ (symbols.csv pins hideAptWindowInternal there and nothing
// defines it), through a raw pointer bridge that keeps the thiscall shape.
void j_0003f3e1();

bool WindowManager::hideAptWindow(int index)
{
	if (static_cast<unsigned int>(index) >= 12)
		return false;

	Slot &window = m_aptWindows[index];
	if (TheMouse)
		TheMouse->setCursorTooltip(UnicodeString::TheEmptyString, 0, 0, 1.0f);

	if (!(window.m_flags & 2))
		return false;

	union { void (*raw)(void); bool (WindowManager::*typed)(int); } hideInternal;
	hideInternal.raw = &j_0003f3e1;
	return (this->*hideInternal.typed)(index);
}
