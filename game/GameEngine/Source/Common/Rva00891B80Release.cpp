// cl: /O2 /Ob0 /DNDEBUG /DWIN32 /D_WINDOWS /MD

struct Rva00891B80Pool
{
	void *m_unused;
	void (__cdecl *free)(void *);
};

struct BfmeStringPool3AF0;
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;

struct Rva00891B80Block
{
	unsigned short m_ref;
};

class Rva00891B80
{
	Rva00891B80Block *m_block;

public:
	void release();
};

void Rva00891B80::release()
{
	Rva00891B80Block *block = m_block;
	if (--block->m_ref == 0)
		(*(Rva00891B80Pool **)&g_rva01337A30AllocPair)->free(block);
}

class Rva00892890
{
	Rva00891B80Block *m_block;

public:
	void release();
};

void Rva00892890::release()
{
	Rva00891B80Block *block = m_block;
	if (--block->m_ref == 0)
		(*(Rva00891B80Pool **)&g_rva01337A30AllocPair)->free(block);
}

class Rva008AD330
{
	Rva00891B80Block *m_block;

public:
	void release();
};

void Rva008AD330::release()
{
	Rva00891B80Block *block = m_block;
	if (--block->m_ref == 0)
		(*(Rva00891B80Pool **)&g_rva01337A30AllocPair)->free(block);
}

class EAStringC { public: class StringDataC; };
extern EAStringC::StringDataC g_rva012D5298Empty;	// shared empty string block 0x012D5298

class Rva00891C10
{
	Rva00891B80Block *m_block;

public:
	void clear();
};

void Rva00891C10::clear()
{
	Rva00891B80Block *block = m_block;
	if (--block->m_ref == 0)
		(*(Rva00891B80Pool **)&g_rva01337A30AllocPair)->free(block);
	m_block = (Rva00891B80Block *)&g_rva012D5298Empty;
	++(*(Rva00891B80Block *)&g_rva012D5298Empty).m_ref;
}
