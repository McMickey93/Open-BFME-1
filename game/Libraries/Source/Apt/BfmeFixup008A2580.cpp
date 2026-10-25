// cl: /DNDEBUG /MD /EHsc
// Open-BFME: loaded-animation pointer fixup, retail 0x008A2130 (1092 B),
// with its existing relative-pointer wrapper at 0x008A2580 (56 B).
// BFME 2 donor: AptAnimation.cpp, 006E5050, revision beed8a16790a.
// These are address-qualified data-format views. BFME 1 offsets and the
// ten-entry dispatch table are independently checked; donor assertions and
// case 12 are not part of this body. Native qualification must verify
// both complete bodies.

typedef unsigned int Word;

class BfmeFixupChunk2580
{
public:
	char m_pad[0x1c];
	int m_rel;
};

// Preserve the canonical callback-cell symbols. Their actual call-site
// contracts are applied locally; no new callback identity is asserted.
extern void (*g_bfmeSlot17VB)();
extern void (*g_bfmeSlot21VB)();
extern void (*g_bfmeSlot24VB)();
typedef Word (__cdecl *Rva008A2130Callback2)(void *, int);
typedef Word (__cdecl *Rva008A2130Callback3)(void *, int, const char *);

struct Rva008D32B0Row;
class Rva0089C860State;
class Rva008D32B0
{
public:
	int m_count;
	Rva008D32B0Row *m_rows;
	Rva0089C860State *m_state;
	void relocate(unsigned base, int arg2, void *arg3);
};

// The generated thunk's full target is independently cdecl with four words.
// Keep the existing linker identity, without adding a routing pin.
extern "C" void __cdecl __identifier("?j_008cc560@@YAXXZ")(
	void *, void *, BfmeFixupChunk2580 *, int *);

class Rva00894D80Accessor
{
public:
	static unsigned increment(unsigned *);
};
class Rva00894D90Accessor
{
public:
	static unsigned decrement(unsigned *);
};
void bfmeDropA(void *);

class RefHandle008958D0
{
public:
	unsigned *m_value;
	RefHandle008958D0(const RefHandle008958D0 &other)
		: m_value(other.m_value)
	{
		if (m_value)
			Rva00894D80Accessor::increment(m_value);
	}
	~RefHandle008958D0()
	{
		if (m_value && Rva00894D90Accessor::decrement(m_value) == 0)
			bfmeDropA(m_value);
	}
	RefHandle008958D0 &operator=(const RefHandle008958D0 &other)
	{
		if (&other != this)
		{
			if (m_value && Rva00894D90Accessor::decrement(m_value) == 0)
				bfmeDropA(m_value);
			m_value = other.m_value;
			if (m_value)
				Rva00894D80Accessor::increment(m_value);
		}
		return *this;
	}
};

struct BfmeStringPool3AF0;
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;
struct Rva008A2130Release
{
	void *m_00;
	void (__cdecl *free)(void *);
};
class BfmeStrVKI
{
public:
	unsigned short *m_data;
	BfmeStrVKI(const char *text) { bfmeSetVKI(text); }
	void __declspec(nothrow) bfmeSetVKI(const char *);
	~BfmeStrVKI()
	{
		unsigned short *data = m_data;
		if (--*data == 0)
			(*(Rva008A2130Release **)&g_rva01337A30AllocPair)->free(data);
	}
};
class Rva00893030Manager
{
public:
	RefHandle008958D0 rva00895A00(BfmeStrVKI *);
};
extern Rva00893030Manager *g_rva00893030Manager;

struct Rva008A2130Export
{
	char *m_name;
	int m_index;
};
struct Rva008A2130Import
{
	char *m_file;
	char *m_name;
	int m_unknown08;
	RefHandle008958D0 m_handle;
};
struct Rva008A2130ActionCondition
{
	unsigned m_flags;
	struct { void *m_stream; } m_actions;
};
struct Rva008A2130StaticTextRecord
{
	char m_pad00[0x34];
	void *m_glyphs34;
};
struct Rva008A2130Character
{
	int m_type;
	Rva008A2130Character *m_parent;
	union
	{
		struct { char m_pad08[0x10]; Word m_value18; } m_case1;
		struct { char m_pad08[0x2c]; char *m_pointer34; char *m_pointer38; } m_case2;
		struct { char *m_pointer08; int m_unknown0c; void *m_pointer10; } m_case3;
		struct
		{
			char m_pad08[0x1c];
			void *m_pointer24;
			void *m_pointer28;
			int m_unknown2c;
			void *m_pointer30;
			int m_count34;
			Rva008A2130ActionCondition *m_conditions38;
			void *m_pointer3c;
		} m_case4;
		Rva008D32B0 m_case5;
		struct { Word m_value08; } m_case6;
		struct { Word m_value08; } m_case7;
		Rva008D32B0 m_case9;
		struct
		{
			char m_pad08[0x28];
			int m_count30;
			Rva008A2130StaticTextRecord *m_records34;
		} m_case10;
	};
};

class BfmeFixup2580
{
public:
	void helper(void *pBase, BfmeFixupChunk2580 *pConstantFile, void *pLoadContext);
	void apply(void *a, BfmeFixupChunk2580 *chunk, void *c);

	char m_pad00[0x0c];
	int m_characterCount;
	Rva008A2130Character **m_characters;
	char m_pad14[0x0c];
	int m_importCount;
	Rva008A2130Import *m_imports;
	int m_exportCount;
	Rva008A2130Export *m_exports;
	int m_flag;
};

// Re-evaluate the original field expression, as the nested retail reloads do.
// A reference-taking helper evaluates the field address only once.
#define RVA008A2130_OFFSET(field) if (field) (unsigned &)(field) += (unsigned)pBase

void BfmeFixup2580::helper(void *pBase, BfmeFixupChunk2580 *pConstantFile,
	void *pLoadContext)
{
	RVA008A2130_OFFSET(m_characters);
	RVA008A2130_OFFSET(m_exports);
	int i;
	for (i = 0; i < m_exportCount; ++i)
	{
		RVA008A2130_OFFSET(m_exports[i].m_name);
	}
	for (i = 0; i < m_characterCount; ++i)
	{
		RVA008A2130_OFFSET(m_characters[i]);
		if (m_characters[i])
		{
			m_characters[i]->m_parent = m_characters[0];
			switch (m_characters[i]->m_type)
			{
			case 1:
				m_characters[i]->m_case1.m_value18 =
					reinterpret_cast<Rva008A2130Callback2>(g_bfmeSlot24VB)(pLoadContext, i);
				break;
			case 2:
				RVA008A2130_OFFSET(m_characters[i]->m_case2.m_pointer34);
				RVA008A2130_OFFSET(m_characters[i]->m_case2.m_pointer38);
				break;
			case 3:
				RVA008A2130_OFFSET(m_characters[i]->m_case3.m_pointer08);
				RVA008A2130_OFFSET(m_characters[i]->m_case3.m_pointer10);
				break;
			case 4:
				{
					RVA008A2130_OFFSET(m_characters[i]->m_case4.m_pointer24);
					RVA008A2130_OFFSET(m_characters[i]->m_case4.m_pointer28);
					RVA008A2130_OFFSET(m_characters[i]->m_case4.m_pointer30);
					RVA008A2130_OFFSET(m_characters[i]->m_case4.m_conditions38);
					for (int j = 0; j < m_characters[i]->m_case4.m_count34; ++j)
					{
						RVA008A2130_OFFSET(m_characters[i]->m_case4.m_conditions38[j].m_actions.m_stream);
						__identifier("?j_008cc560@@YAXXZ")(
							m_characters[i]->m_case4.m_conditions38[j].m_actions.m_stream,
							pBase, pConstantFile, &m_flag);
					}
					RVA008A2130_OFFSET(m_characters[i]->m_case4.m_pointer3c);
				}
				break;
			case 5:
				m_characters[i]->m_case5.relocate((unsigned)pBase, (int)pConstantFile, &m_flag);
				break;
			case 6:
				{
					const char *name = 0;
					for (int j = 0; j < m_exportCount; ++j)
						if (m_exports[j].m_index == i)
							name = m_exports[j].m_name;
					m_characters[i]->m_case6.m_value08 =
						reinterpret_cast<Rva008A2130Callback3>(g_bfmeSlot17VB)(pLoadContext, i, name);
				}
				break;
			case 7:
				m_characters[i]->m_case7.m_value08 =
					reinterpret_cast<Rva008A2130Callback2>(g_bfmeSlot21VB)(pLoadContext, i);
				break;
			case 8:
				break;
			case 9:
				m_characters[i]->m_case9.relocate((unsigned)pBase, (int)pConstantFile, &m_flag);
				break;
			case 10:
				RVA008A2130_OFFSET(m_characters[i]->m_case10.m_records34);
				for (int j = 0; j < m_characters[i]->m_case10.m_count30; ++j)
				{
					RVA008A2130_OFFSET(m_characters[i]->m_case10.m_records34[j].m_glyphs34);
				}
				break;
			default:
				break;
			}
		}
	}
	RVA008A2130_OFFSET(m_imports);
	for (i = 0; i < m_importCount; ++i)
	{
		RVA008A2130_OFFSET(m_imports[i].m_file);
		RVA008A2130_OFFSET(m_imports[i].m_name);
		m_imports[i].m_handle = g_rva00893030Manager->rva00895A00(
			&BfmeStrVKI(m_imports[i].m_file));
	}
}

#undef RVA008A2130_OFFSET

void BfmeFixup2580::apply(void *a, BfmeFixupChunk2580 *chunk, void *c)
{
	BfmeFixupChunk2580 *p = chunk;
	if (p->m_rel != 0)
		p->m_rel += (int)p;
	m_flag = 0;
	helper(a, p, c);
	if (p->m_rel != 0)
		p->m_rel -= (int)p;
}
