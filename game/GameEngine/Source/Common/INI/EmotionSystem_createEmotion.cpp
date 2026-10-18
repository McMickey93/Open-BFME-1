// cl: /DNDEBUG /MD /EHsc

#include <new>

class Object;
class EmotionTrackerUpdateEntry;

// Retail 0x0037CAD0 allocates 0x34 bytes and calls the constructor through
// ILT 0x0002DD08, which jumps to the matched body 0x0037BF60.  The ledger
// carries that body under ??0Rva0037BF60Owner@@QAE@HH@Z, while the pinned
// ??0Emotion@@QAE@PAVObject@@PAVEmotionTrackerUpdateEntry@@@Z has no other
// definition.  Forward through placement construction so the constructor
// symbol exists without changing the byte-exact createEmotion call site.
class Rva0037BF60Owner
{
public:
	Rva0037BF60Owner(int object, int entry);
};

class Emotion
{
public:
	__declspec(noinline) Emotion(Object *object, EmotionTrackerUpdateEntry *entry);

private:
	unsigned char m_unknown00[0x34];
};

__declspec(noinline) Emotion::Emotion(Object *object, EmotionTrackerUpdateEntry *entry)
{
	new (this) Rva0037BF60Owner((int)object, (int)entry);
}

class EmotionSystem
{
public:
	Emotion *createEmotion(EmotionTrackerUpdateEntry *entry, Object *object);
};

// ?createEmotion@EmotionSystem@@QAEPAVEmotion@@PAVEmotionTrackerUpdateEntry@@PAVObject@@@Z
Emotion *EmotionSystem::createEmotion(EmotionTrackerUpdateEntry *entry, Object *object)
{
	if (entry == 0 || object == 0)
		return 0;

	return new Emotion(object, entry);
}
