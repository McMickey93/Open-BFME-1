// ?update@ParticleSystemManager@@UAEXXZ
// partial score=0.9807 date=2026-10-28
// cl: /DNDEBUG /MD /EHsc
// ParticleSystemManager::update, retail 0x005C37E0, 467 B (vtable slot 5 of
// ParticleSystemManager 0x0110FDCC and W3DParticleSystemManager 0x0112039C).
// Zero Hour ParticleSys.cpp:2928 loop (including its `continue` without ++it)
// over BFME's weak BfmeParticleSystemHandle list (layout from the matched
// ParticleSystemManagerReset.cpp), plus QueryPerformanceCounter timing.
// 467/467 B, 9 bytes off: VC7.1 puts `start` at [esp+14h] and `end` at
// [esp+1Ch]; retail has them the other way round. See attempt_support handoff.
typedef bool Bool;
typedef float Real;

union LARGE_INTEGER
{
	struct { unsigned long LowPart; long HighPart; };
	__int64 QuadPart;
};
extern "C" __declspec(dllimport) int __stdcall QueryPerformanceCounter(LARGE_INTEGER *count);
extern "C" __declspec(dllimport) int __stdcall QueryPerformanceFrequency(LARGE_INTEGER *frequency);

class GlobalData
{
public:
	unsigned char m_unmodelled_000[0xA91];
	Bool m_enableFrameTiming;			// +0xA91
};
extern GlobalData *TheWritableGlobalData;

class GameClient
{
public:
	unsigned char m_unmodelled_000[0xC4];
	Bool m_clientFlag;						// +0xC4
};
extern GameClient *TheGameClient;

class GameLogic
{
public:
	unsigned char m_unmodelled_000[0x11D];
	Bool m_gameLogicFlag;						// +0x11D
};
extern GameLogic *TheGameLogic;

struct BfmeParticleSystemHandle;

class ParticleSystem
{
public:
	virtual ~ParticleSystem();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual Bool update(int localPlayerIndex);	// +0x10

	unsigned char m_unmodelled_004[0x94 - 4];
	int m_needsUpdate;					// +0x94
	BfmeParticleSystemHandle *m_handleHead;	// +0x98
	BfmeParticleSystemHandle *m_handleTail;	// +0x9C
};

struct BfmeParticleSystemHandle
{
	BfmeParticleSystemHandle() : m_system(0), m_previous(0), m_next(0) {}
	~BfmeParticleSystemHandle() throw();
	__forceinline BfmeParticleSystemHandle &operator=(const BfmeParticleSystemHandle &other)
	{
		if (this != &other)
		{
			if (m_system)
			{
				if (m_previous)
					m_previous->m_next = m_next;
				else
					m_system->m_handleHead = m_next;
				if (m_next)
					m_next->m_previous = m_previous;
				else
					m_system->m_handleTail = m_previous;
				m_previous = 0;
				m_next = 0;
			}
			m_system = other.m_system;
			if (m_system)
			{
				m_previous = m_system->m_handleTail;
				m_next = 0;
				m_system->m_handleTail = this;
				if (m_previous)
					m_previous->m_next = this;
				else
					m_system->m_handleHead = this;
			}
		}
		return *this;
	}
	ParticleSystem *operator->() const { return m_system; }

	ParticleSystem *m_system;
	BfmeParticleSystemHandle *m_previous;
	BfmeParticleSystemHandle *m_next;
};

struct BfmeParticleSystemNode
{
	BfmeParticleSystemNode *m_next;
	BfmeParticleSystemNode *m_previous;
	BfmeParticleSystemHandle m_value;
};

struct BfmeParticleSystemList
{
	BfmeParticleSystemNode *m_node;
};

class ParticleSystemManager
{
public:
	virtual void update();

private:
	unsigned char m_unmodelled_004[0x08];
	ParticleSystem *m_allParticlesHead[14];
	ParticleSystem *m_allParticlesTail[14];
	unsigned int m_uniqueSystemID;
	BfmeParticleSystemList m_allParticleSystemList;	// +0x80
	unsigned int m_particleCount;
	unsigned int m_fieldParticleCount;
	unsigned int m_particleSystemCount;
	int m_onScreenParticleCount;
	Real m_lastUpdateMilliseconds;					// +0x94
	int m_localPlayerIndex;					// +0x98
};

void ParticleSystemManager::update()
{
	LARGE_INTEGER frequency, start, end;
	m_lastUpdateMilliseconds = 0;
	if (TheWritableGlobalData->m_enableFrameTiming)
	{
		QueryPerformanceFrequency(&frequency);
		QueryPerformanceCounter(&start);
	}

	BfmeParticleSystemHandle sys;
	Bool skipUpdate = TheGameClient->m_clientFlag && !TheGameLogic->m_gameLogicFlag;

	for (BfmeParticleSystemNode *it = m_allParticleSystemList.m_node->m_next;
		it != m_allParticleSystemList.m_node;)
	{
		sys = it->m_value;
		if (!sys.m_system)
			continue;

		if (sys->m_needsUpdate || skipUpdate)
		{
			if (sys->update(m_localPlayerIndex) == false)
			{
				it = it->m_next;
				delete sys.m_system;
				continue;
			}
		}
		it = it->m_next;
	}

	if (TheWritableGlobalData->m_enableFrameTiming)
	{
		QueryPerformanceCounter(&end);
		start.QuadPart = end.QuadPart - start.QuadPart;
		m_lastUpdateMilliseconds = (Real)start.QuadPart * 1000.0f / (Real)frequency.QuadPart;
	}
}
