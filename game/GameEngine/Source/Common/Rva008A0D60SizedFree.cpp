// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc

// Retail VA 0x01337830 is the run-time sized-deallocation callback cell, not an
// import slot; `call dword ptr [0x01337830]` is what these bodies emit.
extern void (__cdecl *TheBfmeFree)(void *storage, unsigned int size);

// Retail VA 0x01337828: the matching run-time allocation callback cell.
extern void *(__cdecl *Rva008C5D70Alloc)(unsigned int bytes);

class Rva008C5B70Buf
{
public:
	void rva008C5B50(unsigned int count);
	void clear();

private:
	int m_pad;
	unsigned int m_count;
	void *m_ptr;
};

// Retail 0x008C5B50, the unreferenced sizing body just before clear():
// record the count and allocate count dwords through the callback cell.
void Rva008C5B70Buf::rva008C5B50(unsigned int count)
{
	m_count = count;
	m_ptr = Rva008C5D70Alloc(count * sizeof(unsigned int));
}

void Rva008C5B70Buf::clear()
{
	if (m_ptr)
		TheBfmeFree(m_ptr, m_count * sizeof(unsigned int));
	m_count = 0;
	m_pad = 0;
	m_ptr = 0;
}

class Rva008C5C40Buf
{
public:
	void rva008C5C20(unsigned int count);
	void clear();

private:
	int m_pad;
	unsigned int m_count;
	void *m_ptr;
};

// Retail 0x008C5C20, the unreferenced sizing body just before clear():
// record the count and allocate count dwords through the callback cell.
void Rva008C5C40Buf::rva008C5C20(unsigned int count)
{
	m_count = count;
	m_ptr = Rva008C5D70Alloc(count * sizeof(unsigned int));
}

void Rva008C5C40Buf::clear()
{
	if (m_ptr)
		TheBfmeFree(m_ptr, m_count * sizeof(unsigned int));
	m_count = 0;
	m_pad = 0;
	m_ptr = 0;
}

class Rva008C5D00Buf
{
public:
	void rva008C5CE0(unsigned int count);
	void clear();

private:
	int m_pad;
	unsigned int m_count;
	void *m_ptr;
};

// Retail 0x008C5CE0, the unreferenced sizing body just before clear():
// record the count and allocate count dwords through the callback cell.
void Rva008C5D00Buf::rva008C5CE0(unsigned int count)
{
	m_count = count;
	m_ptr = Rva008C5D70Alloc(count * sizeof(unsigned int));
}

void Rva008C5D00Buf::clear()
{
	if (m_ptr)
		TheBfmeFree(m_ptr, m_count * sizeof(unsigned int));
	m_count = 0;
	m_pad = 0;
	m_ptr = 0;
}

class Rva008C5DC0Buf
{
public:
	void clear();

private:
	int m_pad;
	unsigned int m_dim1;
	unsigned int m_dim2;
	void *m_ptr;
};

void Rva008C5DC0Buf::clear()
{
	if (m_ptr)
		TheBfmeFree(m_ptr, (m_dim2 * m_dim1) * sizeof(unsigned int));
	m_dim1 = 0;
	m_dim2 = 0;
	m_pad = 0;
	m_ptr = 0;
}
