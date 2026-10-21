// cl: /O2 /Ob0
// TeamInQueue::TeamInQueue, retail 0x00161220 (50 bytes): installs the
// TeamInQueue vtable and clears the 0x30-byte queue node. Open-BFME-2's matched
// constructor is byte-identical and BFME1's ILT slot confirms the name.

class TeamInQueue
{
	void *m_vptr;
	int m_04;
	int m_08;
	int m_0C;
	int m_10;
	int m_14;
	char m_18;
	int m_1C;
	int m_20;
	int m_24;
	char m_28;
	char m_29;
	char m_2A;
	int m_2C;

public:
	TeamInQueue();
};

// Retail vtable VA 0x01096940; the alternate name defines no table.
extern "C" void *__identifier("??_7TeamInQueue@@6B@")[];

TeamInQueue::TeamInQueue()
{
	m_vptr = __identifier("??_7TeamInQueue@@6B@");
	m_04 = 0;
	m_08 = 0;
	m_0C = 0;
	m_10 = 0;
	m_14 = 0;
	m_18 = 0;
	m_1C = 0;
	m_20 = 0;
	m_24 = 0;
	m_28 = 0;
	m_29 = 0;
	m_2A = 0;
	m_2C = 0;
}
