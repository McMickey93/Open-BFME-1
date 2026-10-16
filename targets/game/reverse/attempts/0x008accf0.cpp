// ?bfmeLookup008ACCF0@@YAHPAUBfmeLookupObject008ACCF0@@PAUBfmeLookupString008ACCF0@@E@Z
// partial score=0.9951 date=2026-10-15
// cl: /O2 /MD /DNDEBUG
// ?bfmeLookup008ACCF0@@YAHPAUBfmeLookupObject008ACCF0@@PAUBfmeLookupString008ACCF0@@E@Z
// partial score=0.55 date=2026-09-03
// Open-BFME5 conversion.

extern "C" int __cdecl _strcmpi(const char *a, const char *b);

struct BfmeLookupString008ACCF0Header
{
	char m_padding00[8];
	char m_text[1];
};

struct BfmeLookupString008ACCF0
{
	BfmeLookupString008ACCF0Header *m_header;
 bool matches(const char *p) const { return _strcmpi((const char *)m_header+8,p)==0; }
};

struct BfmeLookupTable008ACCF0
{
	char m_padding00[0x18];
	int *m_resultValues;
	char m_padding1c[0x0C];
	int m_secondCount;
	int *m_secondValues;
	int m_firstCount;
	int *m_firstValues;
};

struct BfmeLookupTableView008ACCF0
{
	char m_padding00[0x10];
	int *m_resultValues;
	char m_padding14[0x0C];
	int m_secondCount;
	int *m_secondValues;
	int m_firstCount;
	int *m_firstValues;
};

struct BfmeLookupTableHolder008ACCF0
{
	char m_padding00[4];
	char *m_table;
};

struct BfmeLookupOwner008ACCF0
{
	char m_padding00[0x0C];
	BfmeLookupTableHolder008ACCF0 *m_holder;
};

struct BfmeLookupObject008ACCF0
{
	char m_padding00[0x4C];
	BfmeLookupObject008ACCF0 *m_next;
	BfmeLookupOwner008ACCF0 *m_owner;
};

int bfmeLookup008ACCF0(BfmeLookupObject008ACCF0 *object,
	BfmeLookupString008ACCF0 *key, unsigned char include)
{
	BfmeLookupString008ACCF0 *needle = key;
	register unsigned char useSecond = include;
	for (;;)
	{
		BfmeLookupTableView008ACCF0 *view = (BfmeLookupTableView008ACCF0 *)
            ((char *)object->m_owner->m_holder->m_table + 8);
        int firstCount = view->m_firstCount;
		int i;
        for(i=0;i<view->m_firstCount;++i)
        {
				if (needle->matches((const char *)view->m_firstValues[i * 2]))
					return view->m_resultValues[view->m_firstValues[i * 2 + 1]];
        }

		if (useSecond != 0)
		{
			int j = 0;
			if (view->m_secondCount > 0)
			{
				do
				{
					if (needle->matches((const char *)view->m_secondValues[j * 4 + 1]))
						return view->m_resultValues[view->m_secondValues[j * 4 + 2]];
					++j;
				} while (j < view->m_secondCount);
			}
		}

		BfmeLookupObject008ACCF0 *next = object->m_next;
        if (next == 0) return 0;
        useSecond = 0;
        object = next;
	}
}
