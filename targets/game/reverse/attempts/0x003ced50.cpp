// ??0LargeGroupAudioMap@@QAE@VAsciiString@@@Z
// partial score=0.9724 date=2026-10-16
// LargeGroupAudioMap(AsciiString) constructor, retail 0x003CED50 (290 bytes, ret 4).
// Exact through +0xD0; only the fstp [esi+0x10] / mov eax,0x7fffffff pair is swapped.
// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
#include "ascii_string.h"
#include <string.h>

class SoundKeyPair;

class SoundKeyVector
{
public:
	SoundKeyVector() : m_begin(0), m_end(0), m_capacity(0) {}
	~SoundKeyVector();

	SoundKeyPair **m_begin;
	SoundKeyPair **m_end;
	SoundKeyPair **m_capacity;
};

struct ConditionFlags
{
	ConditionFlags() { memset(m_value, 0, sizeof(m_value)); }
	unsigned int m_value[10];
};

struct StatusBits
{
	StatusBits() { memset(m_value, 0, sizeof(m_value)); }
	unsigned int m_value[3];
};

class BfmeSinkVUH;

class BfmeBaseVUH
{
public:
	BfmeBaseVUH() : m_owner(0), m_isOverride(0) {}
	virtual ~BfmeBaseVUH();

	BfmeSinkVUH *m_owner;
	unsigned char m_isOverride;
};

static float g_largeGroupAudioSpeedScale = 0.2f;
static const float g_largeGroupAudioSpeedUnit = 20.0f;

struct SpeedCache
{
	void reset()
	{
		m_value[1] = -1.0f;
		m_value[0] = -1.0f;
		m_value[3] = -1.0f;
		m_value[2] = -1.0f;
	}
	float m_value[4];
};

class LargeGroupAudioMap : public BfmeBaseVUH
{
public:
	LargeGroupAudioMap(AsciiString name);
	virtual ~LargeGroupAudioMap();

private:
	float m_size;
	float m_maximumAudioSpeed;
	AsciiString m_soundName;
	SoundKeyVector m_sound;
	ConditionFlags m_requiredModelConditions;
	ConditionFlags m_excludedModelConditions;
	StatusBits m_requiredObjectStatus;
	StatusBits m_excludedObjectStatus;
	int m_startThreshold;
	int m_stopThreshold;
	unsigned short m_handOffModeDuration;
	unsigned char m_ignoreStealthedUnits;
	SpeedCache m_cachedSpeed;
};

LargeGroupAudioMap::LargeGroupAudioMap(AsciiString name) :
	m_soundName(name)
{
	m_cachedSpeed.reset();
	m_startThreshold = 0x7fffffff;
	m_stopThreshold = 0x7fffffff;
	m_maximumAudioSpeed = g_largeGroupAudioSpeedScale * g_largeGroupAudioSpeedUnit;
	m_size = 10000.0f;
	m_handOffModeDuration = 10;
	m_ignoreStealthedUnits = 1;
}
