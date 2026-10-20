// cl: /DNDEBUG /MD /EHsc
#include <ctype.h>
#include <string.h>

static const char *skipIdent(const char *s)
{
	char ch = *s;
	if (ch)
	{
		do
		{
			if (!isalnum(ch) && *s != '_')
				break;
			ch = *++s;
		} while (ch);
	}
	return s;
}

const char *skipIdentAnchor(const char *s)
{
	return skipIdent(s);
}

// Same body as the static at 0x0035E800 (SkipUntilChar.cpp); inlined here.
static const char *skipUntil(const char *p, char delimiter)
{
    char c = *p;
    while (c && c != delimiter)
        c = *++p;
    return p;
}

class LineScanner
{
public:
	const char *skipWhitespace(const char *s);
};

class BfmeLexEAN
{
public:
	int bfmeFailEAN(int code);
};

// One attribute record of the XML tag scanner: NUL-terminated name and
// value copies, 0x61 bytes each, four records from +0x2C.
struct Rva0035E8B0Attribute
{
	char m_name[0x21];
	char m_value[0x40];
};

// The XML reader state shared with BfmeLexEAN (BfmeConv2008.cpp) and the
// XmlNameSlotList accessors; only the fields the tag scanner touches.
class Rva0035E8B0Tail
{
public:
	int scan();

	char *m_pos;
	int m_depth;
	char *m_line;
	int m_lineNumber;
	unsigned char m_emptyTag;
	char *m_buf;
	int m_limit;
	char *m_name;
	char *m_nameEnd;
	char m_nameEndChar;
	int m_attributeCount;
	Rva0035E8B0Attribute m_attributes[4];
};

// Retail 0x0035E8B0 (631 bytes): reached by a tail jump through ILT
// 0x00047C7B from XmlNameSlotList::finish (0x0035EE70) when the cursor is on
// a '<' that does not open a comment. Scans "<name attr='v' ...>" or
// "</name>", returning 1 for an opening tag and 2 for a closing one.
int Rva0035E8B0Tail::scan()
{
	int type = 1;

	m_pos = (char *)((LineScanner *)this)->skipWhitespace(m_pos) + 1;
	m_emptyTag = 0;
	if (*m_pos == 0)
		return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);
	if (*m_pos == '/')
	{
		++m_pos;
		type = 2;
		if (*m_pos == 0)
			return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);
	}

	m_pos = (char *)((LineScanner *)this)->skipWhitespace(m_pos);
	if (*m_pos == 0)
		return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

	m_name = m_pos;
	char *nameEnd = (char *)skipIdent(m_pos);
	m_pos = nameEnd;
	if (*nameEnd == 0)
		return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

	m_pos = (char *)((LineScanner *)this)->skipWhitespace(nameEnd);
	if (*m_pos == 0)
		return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

	m_attributeCount = 0;
	if (type == 1 && isalnum(*m_pos))
	{
		do
		{
			char *attributeName = m_pos;
			char *attributeNameEnd = (char *)skipIdent(m_pos);
			m_pos = attributeNameEnd;
			if (*attributeNameEnd == 0)
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			m_pos = (char *)((LineScanner *)this)->skipWhitespace(attributeNameEnd);
			if (*m_pos == 0 || *m_pos != '=')
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			++m_pos;
			if (*m_pos == 0)
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			m_pos = (char *)((LineScanner *)this)->skipWhitespace(m_pos);
			char quote = *m_pos;
			if (quote == 0 || (quote != '"' && quote != '\''))
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			++m_pos;
			if (*m_pos == 0)
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			char *value = m_pos;
			char *valueEnd = (char *)skipUntil(m_pos, quote);
			m_pos = valueEnd;
			if (*valueEnd == 0)
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			m_pos = valueEnd + 1;
			if (*m_pos == 0)
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			m_pos = (char *)((LineScanner *)this)->skipWhitespace(m_pos);
			if (*m_pos == 0)
				return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);

			if (m_attributeCount < 4)
			{
				char saved = *attributeNameEnd;
				*attributeNameEnd = 0;
				strncpy(m_attributes[m_attributeCount].m_name, attributeName, 0x20);
				m_attributes[m_attributeCount].m_name[0x20] = 0;
				*attributeNameEnd = saved;

				saved = *valueEnd;
				*valueEnd = 0;
				strncpy(m_attributes[m_attributeCount].m_value, value, 0x3F);
				m_attributes[m_attributeCount].m_value[0x3F] = 0;
				*valueEnd = saved;

				++m_attributeCount;
			}
		} while (isalnum(*m_pos));
	}

	if (*m_pos == '/')
	{
		m_emptyTag = 1;
	}
	else
	{
		if (*m_pos != '>')
			return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);
		++m_pos;
	}

	m_nameEnd = nameEnd;
	m_nameEndChar = *nameEnd;
	*nameEnd = 0;
	if (type == 1)
		++m_depth;
	else
		--m_depth;
	return type;
}
