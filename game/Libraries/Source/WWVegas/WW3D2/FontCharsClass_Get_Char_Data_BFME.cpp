#include "Rva0093DCE0TreeFind.h"

struct FontCharsClassCharDataStruct;

struct FontCharDataMapNode
{
	char fields[0x14];
	const FontCharsClassCharDataStruct *value;
};

class FontCharDataMap
{
public:
	FontCharDataMapNode *m_end;
};

class FontCharsClass
{
public:
	const FontCharsClassCharDataStruct *Get_Char_Data(unsigned short character);

private:
	char m_fields00[8];
	FontCharsClass *m_alternateUnicodeFont;
	char m_fields0C[0x444];
	FontCharDataMap m_characterData;
};

// The loader at 0x00940D40 is linked as the gen-dump ?d_00940d40@@YAXXZ, so the
// thiscall is reached through a member-pointer call (the pattern the Apt
// callers of ?d_008cc940 use).
extern void d_00940d40();
typedef const FontCharsClassCharDataStruct *(FontCharsClass::*FontCharsLoadCharacterData)(unsigned short character);

const FontCharsClassCharDataStruct *FontCharsClass::Get_Char_Data(
	unsigned short character)
{
	union { void (*fn)(); FontCharsLoadCharacterData call; } loadCharacterData = { d_00940d40 };
	unsigned short originalCharacter = character;
	FontCharsClass *font = this;
	for (;;)
	{
		FontCharDataMap *map = &font->m_characterData;
		const FontCharsClassCharDataStruct *data;
		FontCharDataMapNode *node = reinterpret_cast<FontCharDataMapNode *>(
			reinterpret_cast<const Rva0093DCE0Tree *>(map)->find(character));
		if (node == map->m_end || (data = node->value) == 0)
			data = (font->*loadCharacterData.call)(originalCharacter);
		if (data != reinterpret_cast<const FontCharsClassCharDataStruct *>(-1))
			return data;
		FontCharsClass *alternate = font->m_alternateUnicodeFont;
		if (alternate == 0 || font == alternate)
			return 0;
		font = alternate;
	}
}
