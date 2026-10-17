// ?bfmeRemoveObjectA1C20@BfmeJ1017@@QAEXPAVBfmeObj4310@@@Z
// partial score=0.2857 date=2026-10-18
// cl: /O2 /DNDEBUG /MD
// BFME object-removal helper reached by BfmeObj4310::bfmeCleanup at 0x008C3F10.
// The caller leaves the BfmeJ1017 holder in ECX and passes the object on the
// stack; the holder's 0x20-byte entries are drained through releaseAll.

class Rva008A0FF0ValueStack
{
public:
	void releaseAll(void);
};

class BfmeEntryA1C20
{
public:
	virtual void slot00(void) = 0;
	virtual void release(void) = 0;

	union
	{
		unsigned int m_flags;
		struct { unsigned m_type:6; unsigned m_bits06:9; unsigned m_valid15:1; };
	};
	char m_gap08[0x1c];
	int m_key;

	int isType10()
	{
		bool undefined = !m_valid15;
		if (m_type == 10 && !undefined)
			return 1;
		return 0;
	}
};

class BfmeObjectStateA1C20
{
public:
	char m_gap00[0x0c];
	int m_key;
};

class BfmeObj4310
{
public:
	char m_gap00[0x50];
	BfmeObjectStateA1C20 *m_state;
};

struct BfmeSlotA1C20
{
	void *m_value;
	BfmeEntryA1C20 *m_entry;
	char m_gap08[0x18];
};

class BfmeJ1017
{
public:
	char m_gap00[0x1230];
	BfmeSlotA1C20 *m_slots;
	int m_count;
	char m_gap1238[0x6c];
	int m_limit;

	void bfmeRemoveObjectA1C20(BfmeObj4310 *object);
};

struct BfmePickWorld1284
{
	char m_gap00[0x12a4];
	int m_limit;
};

extern BfmePickWorld1284 *g_bfmeHolderBU;

void BfmeJ1017::bfmeRemoveObjectA1C20(BfmeObj4310 *object)
{
	int remaining = m_count;
	if (remaining == 0)
		return;

	for (int index = 0; index < g_bfmeHolderBU->m_limit; ++index)
	{
		BfmeSlotA1C20 *slot = &m_slots[index];
		if (slot->m_value == 0)
			continue;

		BfmeObjectStateA1C20 *state = object->m_state;
		if (state != 0)
		{
			if (slot->m_entry->isType10() && slot->m_entry->m_key == state->m_key)
			{
				slot->m_entry->release();
				((Rva008A0FF0ValueStack *)&m_slots[index])->releaseAll();
				m_slots[index].m_value = 0;
				--m_count;
			}
		}
		if (--remaining == 0)
			break;
	}
}

