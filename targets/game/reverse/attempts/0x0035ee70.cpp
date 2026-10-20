// ?finish@XmlNameSlotList@@QAEHXZ
// partial score=0.811 date=2026-10-20
class BfmeLexEAO
{
public:
	char bfmeSkipCommentEAO();

	char *m_bfmePosEAO;
};

char BfmeLexEAO::bfmeSkipCommentEAO()
{
	char *p = m_bfmePosEAO + 2;

	m_bfmePosEAO = p;

	if (*p != 0x2d)
		return 0;

	p++;
	m_bfmePosEAO = p;

	if (*p != 0x2d)
		return 0;

	p++;
	m_bfmePosEAO = p;

	if (*p == 0)
		return 0;

	for (;;)
	{
		char *q = m_bfmePosEAO;
		char c = *q;

		while (c != 0 && c != 0x2d)
		{
			c = q[1];
			q++;
		}

		m_bfmePosEAO = q;

		if (*q == 0)
			return 0;

		q++;
		m_bfmePosEAO = q;

		c = *q;

		if (c == 0)
			return 0;

		if (c == 0x2d)
		{
			q++;
			m_bfmePosEAO = q;

			c = *q;

			if (c == 0)
				return 0;

			if (c == 0x3e)
			{
				q++;
				m_bfmePosEAO = q;

				return 1;
			}
		}
	}
}

extern "C" void _WriteBarrier(void);
extern "C" void _ReadWriteBarrier(void);
extern "C" void _ReadBarrier(void);
#pragma intrinsic(_WriteBarrier, _ReadWriteBarrier, _ReadBarrier)

class LineScanner
{
public:
	const char *skipWhitespace(const char *s);
};

class BfmeLexEAN
{
public:
	int bfmeFailEAN(int code);
	int bfmeScanEAN();
};

class Rva0035E8B0Tail
{
public:
	int scan();
};

// The XML reader's token step: same object as BfmeLexEAN and the tag
// scanner; only the fields this body touches.
class XmlNameSlotList
{
public:
	int finish();

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
};

int XmlNameSlotList::finish()
{
	if (m_emptyTag != 0 && *m_pos == '/')
	{
		++m_pos;
		if (*m_pos != '>')
		{
			_ReadWriteBarrier();
			return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);
		}
		++m_pos;
		return 2;
	}

	if (m_nameEnd != 0)
	{
		*m_nameEnd = m_nameEndChar;
		m_nameEnd = 0;
		m_nameEndChar = 0;
	}

	if (m_pos == 0)
	{
		/*B2*/
		return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);
	}

	while (*(m_pos = (char *)((LineScanner *)this)->skipWhitespace(m_pos)) != 0)
	{
		if (*m_pos == '<')
		{
			if (m_pos[1] != '!')
				return ((Rva0035E8B0Tail *)this)->scan();
		}
		else
			return ((BfmeLexEAN *)this)->bfmeScanEAN();
		if (!((BfmeLexEAO *)this)->bfmeSkipCommentEAO())
		{
			_WriteBarrier();
			return ((BfmeLexEAN *)this)->bfmeFailEAN(-1);
		}
	}
	m_name = 0;
	m_attributeCount = 0;
	return 0;
}
