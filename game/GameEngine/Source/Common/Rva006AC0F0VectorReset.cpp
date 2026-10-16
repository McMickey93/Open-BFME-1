// cl: /O2 /EHsc /DNDEBUG /DWIN32 /D_WINDOWS /MD
// Retail 0x006AC0F0: lock the owner, erase an AsciiString key from the
// AudioEventInfo table at +0x70 (Zero Hour AudioEventInfoHash, the slot after
// findAudioEventInfo in the AudioManager vtable), and invalidate the ready flag.
// identity_evidence/006a78c0-ascii-hash-erase-not-buildablestatus.md

extern "C" __declspec(dllimport) unsigned long __stdcall WaitForSingleObject(
	void *handle, unsigned long milliseconds);
extern "C" __declspec(dllimport) int __stdcall ReleaseMutex(void *handle);

class AsciiString;
class AudioEventInfo;
namespace rts { template <class Key> struct hash; template <class Key> struct equal_to; }
namespace _STL
{
template <class First, class Second> struct pair;
template <class Value> struct _Select1st;
template <class Key> struct equal_to;
template <class Value> class allocator;
template <class Value, class Key, class Hash, class Extract, class Equal, class Alloc>
class hashtable
{
public:
    unsigned int erase(const Key &);
};
}

class Rva006AC0F0MutexGuard
{
public:
	Rva006AC0F0MutexGuard(void *handle)
	{
		m_owned = 0;
		m_handle = handle;
		if (WaitForSingleObject(handle, 0xFFFFFFFF) != 0x102)
			m_owned = 1;
	}

	~Rva006AC0F0MutexGuard()
	{
		if (m_owned)
			ReleaseMutex(m_handle);
	}

private:
	void *m_handle;
	char m_owned;
};

class Rva006AC0F0Owner
{
public:
	void resetVector(int index);

private:
	char m_pad70[0x70];
	char m_pad630[0x630 - 0x70];
	unsigned char m_ready;
	char m_pad631[0x95c - 0x631];
	void *m_mutex;
};

void Rva006AC0F0Owner::resetVector(int index)
{
	Rva006AC0F0Owner *self = this;
	void *handle = self->m_mutex;
	Rva006AC0F0MutexGuard guard(handle);
    reinterpret_cast<_STL::hashtable<_STL::pair<const AsciiString, AudioEventInfo *>,
        AsciiString, rts::hash<AsciiString>,
        _STL::_Select1st<_STL::pair<const AsciiString, AudioEventInfo *> >,
        rts::equal_to<AsciiString>,
        _STL::allocator<_STL::pair<const AsciiString, AudioEventInfo *> > > *>(
            reinterpret_cast<char *>(self) + 0x70)
        ->erase(*reinterpret_cast<const AsciiString *>(index + 8));
	self->m_ready = 0;
}
