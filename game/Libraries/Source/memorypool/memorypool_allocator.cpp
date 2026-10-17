// Address-derived identity; this is the block-integrity helper called by
// MemoryPool::_VerifyIntegrity at 0x00882D50.
// cl: /O2 /DNDEBUG /MD /Oa

unsigned char bfmeAllSame(
	const unsigned int *data, unsigned int value, unsigned int bytes);
extern void __cdecl memset32(void *ptr, int value, unsigned int bytesToFill);
// Retail check (RVA 0x00882580, 174 bytes) reads these as two dwords
// at VA 0x0130EA00/0x0130EA04 and one byte at VA 0x0130E9F9.
// All three scalars are initially zero in retail .data; data_rows.csv
// verifies their widths and initial bytes independently of the code match.
int Rva0130EA00GuardWords = 0;
unsigned int g_rva0130EA04 = 0;
unsigned char g_rva0130E9F9 = 0;

class Rva008838F0Owner
{
public:
	void rva008836F0(void *block, char *diagnostic, unsigned int limit);
};
extern Rva008838F0Owner g_bfmeRva0130EA10Owner;

class Rva00882580Block
{
public:
	unsigned char check(void);
	void setUsed(int used);
	void *guardStart(void);
	void rva008824E0(unsigned int size);
private:
	void *m_field00;
	void *m_field04;
	unsigned int m_size08;
};

unsigned char Rva00882580Block::check(void)
{
	char diagnostic[0x1000];
	unsigned char good = 1;
	unsigned int guardWords = *(volatile unsigned int *)&Rva0130EA00GuardWords;

	if (guardWords != 0)
	{
		unsigned int guardBytes = guardWords * 4;
		if (bfmeAllSame(
			(const unsigned int *)((unsigned int)this - guardBytes),
			0x0BADF00D, guardBytes) == 0)
			good = 0;
		if (bfmeAllSame(
			(const unsigned int *)((unsigned int)this + m_size08 + 0x0c),
			0x0BADF00D, guardBytes) == 0)
			good = 0;
	}

	if (m_field00 == 0 && *(volatile unsigned int *)&g_rva0130EA04 != 0)
	{
		if (bfmeAllSame(
			(const unsigned int *)((unsigned int)this + 0x0c),
			0xDEADC0DE, m_size08) == 0)
			goto report;
	}

	if (good != 0)
		return 1;

report:
	if (*(volatile unsigned char *)&g_rva0130E9F9 != 0)
		g_bfmeRva0130EA10Owner.rva008836F0(
			(unsigned char *)this + 0x0c, diagnostic, 0x1000);
	return 1;
}

// Retail 0x008824E0 (104 bytes, __thiscall, ret 4): reset a block header to
// an unused block of `size` payload bytes, refill both guard bands and, when
// free-poisoning is on, poison the payload. Address-derived name.
void Rva00882580Block::rva008824E0(unsigned int size)
{
	m_field00 = 0;
	m_size08 = size;
	if (Rva0130EA00GuardWords != 0)
	{
		unsigned int guardBytes = Rva0130EA00GuardWords * 4;
		memset32((char *)this - guardBytes, 0x0BADF00D, guardBytes);
		memset32((char *)this + m_size08 + 0x0c, 0x0BADF00D, guardBytes);
	}
	if (g_rva0130EA04 != 0)
		memset32((char *)this + 0x0c, 0xDEADC0DE, m_size08);
}

void Rva00882580Block::setUsed(int used)
{
	m_size08 = used;
	if (Rva0130EA00GuardWords)
		memset32((char *)this + used + 0x0c, 0x0BADF00D, Rva0130EA00GuardWords * 4);
}

void *Rva00882580Block::guardStart(void)
{
	return (char *)this - Rva0130EA00GuardWords * 4;
}
