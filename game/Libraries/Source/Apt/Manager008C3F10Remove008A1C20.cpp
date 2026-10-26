// cl: /O2 /DNDEBUG /MD
// Retail 0x008A1C20 (196 bytes, RET 4 at +0xC1). The matched caller
// Rva008C3F10Value::cleanup (AptCIH.cpp, call at 0x008C3F10+0x114) names it
// Manager008C3F10::remove008A1C20 and passes the dying value with ECX holding
// the manager at 0x013377D8. It walks the manager's 32-byte slot table at
// +0x1230 up to the holder's slot limit at +0x12A4, visiting at most the
// live-slot count at +0x1234 occupied slots; a slot whose +4 value is a valid
// type-10 Apt value keyed like the dying value's state is released, drained
// through Rva008A0FF0ValueStack::releaseAll and cleared.

class Rva008A0FF0ValueStack
{
public:
	void releaseAll();
};

class Rva008A1C20Entry
{
public:
	virtual void slot00();
	virtual void release();

	union
	{
		unsigned int m_flags;
		struct
		{
			unsigned m_type : 6;
			unsigned m_bits06 : 9;
			unsigned m_valid15 : 1;
		};
	};
	char m_gap08[0x1C];
	int m_key;

	bool isType10()
	{
		bool undefined = !m_valid15;
		return m_type == 10 && !undefined;
	}
};

struct Rva008A1C20State
{
	char m_gap00[0x0C];
	int m_key;
};

class Rva008C3F10Value
{
public:
	char m_gap00[0x50];
	Rva008A1C20State *m_state;
};

struct Rva008A1C20Slot
{
	void *m_value;
	Rva008A1C20Entry *m_entry;
	char m_gap08[0x18];
};

struct Manager008C3F10
{
	char m_gap00[0x1230];
	Rva008A1C20Slot *m_slots;
	int m_liveSlots;

	void remove008A1C20(Rva008C3F10Value *object);
};

// retail 0x013377D8; its one definition is ?g_bfmeHolderBU@@3PAUBfmePickWorld1284@@A
struct BfmePickWorld1284;
extern BfmePickWorld1284 *g_bfmeHolderBU;

void Manager008C3F10::remove008A1C20(Rva008C3F10Value *object)
{
	int remaining = m_liveSlots;
	if (remaining == 0)
		return;

	for (int index = 0; index < *(int *)((char *)g_bfmeHolderBU + 0x12A4); ++index)
	{
		if (m_slots[index].m_value == 0)
			continue;

		Rva008A1C20State *state = object->m_state;
		if (state != 0)
		{
			if (m_slots[index].m_entry->isType10() && m_slots[index].m_entry->m_key == state->m_key)
			{
				m_slots[index].m_entry->release();
				((Rva008A0FF0ValueStack *)&m_slots[index])->releaseAll();
				m_slots[index].m_value = 0;
				--m_liveSlots;
			}
		}
		if (--remaining == 0)
			break;
	}
}
