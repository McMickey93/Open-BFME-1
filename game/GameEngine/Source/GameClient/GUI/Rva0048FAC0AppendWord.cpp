// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
// Body at 0x0048FAC0 (__thiscall, RET 12): appends spaces and a word to a text
// line, measures it through the line's DisplayString and wraps via 0x0048F8C0.
// Body at 0x0048F8C0 (__thiscall, RET 4): moves the finished line into the
// owner's entry list.
// Body at 0x0048F5C0 (__thiscall, RET 8): the entry constructor, which splits
// the text into width-limited segments.

#define _STLP_NO_EXCEPTIONS 1
#include <vector>

#include <wchar.h>
#include "string_base.h"
template<> inline bool StringBase<unsigned short>::isEmpty() const { return !m_data || m_data->length == 0; }
template<> inline bool StringBase<unsigned short>::isNotEmpty() const { return getLength() != 0; }
template<> inline unsigned short StringBase<unsigned short>::getCharAt(int index) const { return m_data ? peek()[index] : 0; }
#include "unicode_string.h"

inline UnicodeString::UnicodeString() : m_text(0) {}
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
	virtual void slot40(); virtual void slot44(); virtual void slot48(); virtual void slot4C(); virtual void slot50(); virtual void slot54();
	virtual void slot58(wchar_t c);
};

// Local view of the DisplayStringManager at 0x012F12CC (the slots
// game/GameEngine/Source/GameClient/GUI/IngameNoticeDisplay.cpp also calls).
class DisplayStringManager;
extern DisplayStringManager *TheDisplayStringManager;
class Rva0048F5C0StringManagerView {
public:
	virtual void f0(); virtual void f1(); virtual void f2(); virtual void f3();
	virtual void f4(); virtual void f5(); virtual void f6(); virtual void f7();
	virtual void f8();
	virtual DisplayString *create(void);
	virtual void release(DisplayString *string);
};

// The matched 0x0048EC80 constructor (IngameNoticeDisplay.cpp); retail
// allocates 0x18 bytes for it, of which that TU models the first 0x10.
class Rva0048EC80UnicodeString;
struct Rva0048EC80Descriptor;
class Rva0048EC80ResourceOwner {
public:
	Rva0048EC80ResourceOwner(const Rva0048EC80UnicodeString &text,
		Rva0048EC80Descriptor *descriptor, int identifier);
private:
	char m_unmodelled000[0x18];
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

// Owner +0x08 context: +0x04 font, vtable slot 0x0C the width limit.
struct Rva0048F5C0Context {
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual unsigned int slot0C();
	GameFont *m_font;
};

// 0x14-byte entry built from a finished line's text (constructor 0x0048F5C0
// through ILT 0x0002FF63).
class Rva0048F5C0Entry {
public:
	Rva0048F5C0Entry(const UnicodeString &text, Rva0048F5C0Context *context);
private:
	_STL::vector<Rva0048EC80ResourceOwner *> m_segments;	// +0x00
	char m_unmodelled00C[0x08];
};

// Measures the text one character at a time and cuts a new segment each
// time the width passes the context's limit.
Rva0048F5C0Entry::Rva0048F5C0Entry(const UnicodeString &text, Rva0048F5C0Context *context)
{
	int length = text.getLength();
	if (length == 0)
		return;
	DisplayString *measure = ((Rva0048F5C0StringManagerView *)TheDisplayStringManager)->create();
	GameFont *font = context->m_font;
	measure->setFont(font);
	UnicodeString segment;
	unsigned int maxWidth = context->slot0C();
	int width = maxWidth;
	int index = 0;
	while (length > 0) {
		wchar_t c = text.getCharAt(index++);
		measure->slot58(c);
		int textWidth, textHeight;
		measure->getSize(&textWidth, &textHeight);
		if (textWidth > maxWidth) {
			m_segments.push_back(new Rva0048EC80ResourceOwner(
				*(const Rva0048EC80UnicodeString *)&segment,
				(Rva0048EC80Descriptor *)context, width));
			width = textWidth - width;
			((StringBase<unsigned short> *)&segment)->clear();
			segment += c;
			measure->setText(segment);
		} else {
			width = textWidth;
			segment += c;
		}
		--length;
	}
	if (segment.isNotEmpty())
		m_segments.push_back(new Rva0048EC80ResourceOwner(
			*(const Rva0048EC80UnicodeString *)&segment,
			(Rva0048EC80Descriptor *)context, width));
	((Rva0048F5C0StringManagerView *)TheDisplayStringManager)->release(measure);
}

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
