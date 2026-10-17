// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
// Body at 0x0048FAC0 (__thiscall, RET 12): appends spaces and a word to a text
// line, measures it through the line's DisplayString and wraps via 0x0048F8C0.
// Body at 0x0048F8C0 (__thiscall, RET 4): moves the finished line into the
// owner's entry list.

#define _STLP_NO_EXCEPTIONS 1
#include <vector>

#include <wchar.h>
#include "string_base.h"
template<> inline bool StringBase<unsigned short>::isEmpty() const { return !m_data || m_data->length == 0; }
#include "unicode_string.h"

inline UnicodeString::UnicodeString(const UnicodeString &s) { ((StringBase<unsigned short>*)this)->StringBase<unsigned short>::StringBase(*(const StringBase<unsigned short>*)&s); }
inline UnicodeString::~UnicodeString() { ((StringBase<unsigned short>*)this)->~StringBase<unsigned short>(); }
inline UnicodeString &UnicodeString::operator=(const UnicodeString &s) { ((StringBase<unsigned short>*)this)->set(*(const StringBase<unsigned short>*)&s); return *this; }
inline UnicodeString &UnicodeString::operator+=(wchar_t c) { ((StringBase<unsigned short>*)this)->concat((const unsigned short*)&c, 1); return *this; }
inline UnicodeString &UnicodeString::operator+=(const UnicodeString &s) { ((StringBase<unsigned short>*)this)->concat((const unsigned short*)s.str(), s.getLength()); return *this; }

class GameFont;

class DisplayString {
public:
	virtual ~DisplayString();
	virtual void setText(UnicodeString text);
	virtual UnicodeString getText();
	virtual int getTextLength();
	virtual void notifyTextChanged();
	virtual void reset();
	virtual void setFont(GameFont*);
	virtual GameFont *getFont();
	virtual void setWordWrap(int);
	virtual void setWordWrapCentered(bool);
	virtual void slot28(); virtual void slot2C(); virtual void slot30(); virtual void slot34(); virtual void slot38();
	virtual void getSize(int *width, int *height);
};

// A line record: +0x00 width limit, +0x04 x offset, +0x08 offset list,
// +0x0C display string, +0x10 text, +0x14 measured width.
struct Rva0048FAC0Line {
	int m_maxWidth;
	int m_x;
	_STL::vector<int> *m_offsets;
	DisplayString *m_displayString;
	UnicodeString m_text;
	int m_width;
};

struct Rva0048F5C0Context;

// 0x14-byte entry built from a finished line's text (constructor 0x0048F5C0
// through ILT 0x0002FF63).
class Rva0048F5C0Entry {
public:
	Rva0048F5C0Entry(const UnicodeString &text, Rva0048F5C0Context *context);
private:
	char m_unmodelled000[0x14];
};

class Rva0048FAC0Owner {
public:
	void appendWord(Rva0048FAC0Line *line, int spaces, const UnicodeString &word);
	void flushLine(Rva0048FAC0Line *line);
private:
	char m_unmodelled000[0x08];
	Rva0048F5C0Context *m_context;					// +0x08
	_STL::vector<Rva0048F5C0Entry *> m_entries;			// +0x0C
};

// Wraps the line's text in a new entry, appends it to the owner's list,
// records the line's x offset less half its width, then empties the line.
void Rva0048FAC0Owner::flushLine(Rva0048FAC0Line *line)
{
	m_entries.push_back(new Rva0048F5C0Entry(line->m_text, m_context));
	line->m_offsets->push_back(line->m_x - line->m_width / 2);
	((StringBase<unsigned short> *)&line->m_text)->clear();
	line->m_width = 0;
}

void Rva0048FAC0Owner::appendWord(Rva0048FAC0Line *line, int spaces, const UnicodeString &word)
{
	UnicodeString text(line->m_text);
	for (int i = 0; i < spaces; ++i)
		text += L' ';
	text += word;
	line->m_displayString->setText(text);
	int width, height;
	line->m_displayString->getSize(&width, &height);
	if (width > line->m_maxWidth) {
		if (!line->m_text.isEmpty()) {
			flushLine(line);
			line->m_displayString->setText(word);
			line->m_displayString->getSize(&width, &height);
		} else if (spaces > 0) {
			appendWord(line, 0, word);
			return;
		}
	}
	line->m_text = line->m_displayString->getText();
	line->m_width = width;
}
