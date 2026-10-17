// ?rva008833C0@Rva008838F0Owner@@QAAXHPAXIPBDZZ
// partial score=0.3924 date=2026-10-17
// cl: /O2 /DNDEBUG /MD
// ?rva008839B0@Rva008838F0Owner@@QAEXHPAX@Z
// Address-derived identity. MemoryPool::_Free (0x00882BA0) calls this with
// ECX = the tracker owner at 0x0130EA10 (the same object whose isValidBlock
// is matched in memorypool_tracker.cpp) and pushes its AllocType argument or
// 0xFFFFFD66 plus the block pointer. The bucket table, slot ring, disabled
// flag and lock use that TU's witnessed owner layout.

#include <stdarg.h>
#include <string.h>

extern "C" __declspec(dllimport) void __stdcall EnterCriticalSection(void *lock);
extern "C" __declspec(dllimport) void __stdcall LeaveCriticalSection(void *lock);
extern "C" __declspec(dllimport) void *__stdcall GetProcessHeap(void);
extern "C" __declspec(dllimport) int __stdcall HeapFree(
	void *heap, unsigned long flags, void *block);
extern "C" __declspec(dllimport) void *__stdcall HeapAlloc(
	void *heap, unsigned long flags, unsigned long bytes);
extern "C" __declspec(dllimport) int __cdecl _vsnprintf(
	char *buffer, unsigned int count, const char *format, va_list args);

// The tracker's stack capture (debug_stack.cpp): a signature holds up to 256
// return addresses behind its count.
class DebugStackwalk
{
public:
	class Signature
	{
	public:
		Signature(void) : m_numAddr(0) {}
		unsigned GetAddress(int n) const;

	private:
		unsigned m_numAddr;
		unsigned m_addr[256];
	};

	static int StackWalk(Signature &sig, struct _CONTEXT *ctx, bool useFallback);
};

// Retail 0x01336CDC: running serial stamped on each new tracker node.
extern unsigned int g_Va01336CDC;

class Rva008838F0Node
{
public:
	Rva008838F0Node *m_next;
	unsigned int m_type;
	unsigned int m_key;
	unsigned int m_size;
	unsigned int m_serial;
	void *m_description;
	unsigned int m_count;
	unsigned int m_values[32];
	int m_freeCheckpoint;
};

class Rva008838F0Owner
{
public:
	void rva008839B0(int type, void *block);
	void __cdecl rva008833C0(int type, void *block, unsigned int size, const char *format, ...);
	void __cdecl rva008835C0(void *block, const char *format, ...);

private:
	char m_pad00[0x0c];
	Rva008838F0Node *m_buckets[0x2b7b];
	Rva008838F0Node *m_slots[0x7530];
	unsigned int m_slotIndex;
	Rva008838F0Node *m_current;
	unsigned char m_disabled;
	char m_pad282c1[7];
	void *m_lock;
};

void Rva008838F0Owner::rva008839B0(int type, void *block)
{
	if (m_disabled)
		return;

	if (m_lock != 0)
		EnterCriticalSection(m_lock);

	Rva008838F0Node **link = &m_buckets[(unsigned int)block % 0x2b7b];
	while (*link != 0 && (*link)->m_key != (unsigned int)block)
		link = &(*link)->m_next;

	Rva008838F0Node *node = *link;
	if (node == 0)
	{
		if (m_lock != 0)
			LeaveCriticalSection(m_lock);
		return;
	}
	if (node->m_freeCheckpoint >= 0)
	{
		if (m_lock != 0)
			LeaveCriticalSection(m_lock);
		return;
	}

	Rva008838F0Node *old = m_slots[m_slotIndex];
	if (old != 0)
	{
		Rva008838F0Node **oldLink = &m_buckets[old->m_key % 0x2b7b];
		Rva008838F0Node *cur = *oldLink;
		while (cur != 0 && cur != old)
		{
			oldLink = &(*oldLink)->m_next;
			cur = *oldLink;
		}
		*oldLink = old->m_next;
		old->m_next = m_current;
		if (old->m_description != 0)
		{
			HeapFree(GetProcessHeap(), 0, old->m_description);
			old->m_description = 0;
		}
		m_current = old;
	}
	node->m_freeCheckpoint = m_slotIndex;
	m_slots[m_slotIndex] = node;
	if (++m_slotIndex == 0x7530)
		m_slotIndex = 0;

	if (m_lock != 0)
		LeaveCriticalSection(m_lock);
}

// Retail 0x008835C0 (294 bytes): variadic __cdecl owner method, owner on the
// stack. For a tracked block whose node is still live (negative free
// checkpoint), free its +0x14 text and replace it with the formatted
// description, or clear it when no format is given. Same bucket walk, lock
// and early-unlock exits as rva008839B0 above. Address-derived name.
void __cdecl Rva008838F0Owner::rva008835C0(void *block, const char *format, ...)
{
	char buffer[512];

	if (m_disabled)
		return;

	if (m_lock != 0)
		EnterCriticalSection(m_lock);

	Rva008838F0Node **link = &m_buckets[(unsigned int)block % 0x2b7b];
	while (*link != 0 && (*link)->m_key != (unsigned int)block)
		link = &(*link)->m_next;

	Rva008838F0Node *node = *link;
	if (node == 0 || node->m_freeCheckpoint >= 0)
	{
		if (m_lock != 0)
			LeaveCriticalSection(m_lock);
		return;
	}

	if (node->m_description != 0)
		HeapFree(GetProcessHeap(), 4, node->m_description);
	if (format != 0)
	{
		va_list args;
		va_start(args, format);
		if (_vsnprintf(buffer, sizeof(buffer), format, args) < 0)
			buffer[511] = 0;
		va_end(args);
		unsigned int length = (unsigned int)strlen(buffer) + 1;
		node->m_description = HeapAlloc(GetProcessHeap(), 4, length);
		memcpy(node->m_description, buffer, length);
	}
	else
		node->m_description = 0;

	if (m_lock != 0)
		LeaveCriticalSection(m_lock);
}

// Retail 0x008833C0 (502 bytes): variadic __cdecl owner method, owner on the
// stack; MemoryPool::_Allocate calls it for every block when tracking is on.
// A node still live (negative free checkpoint) is left alone. A node parked
// in the delayed-free ring is unlinked, recycled and its text freed. The
// block then gets a node (recycled or HeapAlloc'd) at the head of its bucket
// with type, size, a serial, the formatted description and up to 32 return
// addresses. Address-derived name.
void __cdecl Rva008838F0Owner::rva008833C0(int type, void *block, unsigned int size, const char *format, ...)
{
	char buffer[512];

	if (m_disabled)
		return;

	if (m_lock != 0)
		EnterCriticalSection(m_lock);

	Rva008838F0Node **link = &m_buckets[(unsigned int)block % 0x2b7b];
	while (*link != 0 && (*link)->m_key != (unsigned int)block)
		link = &(*link)->m_next;

	Rva008838F0Node *node = *link;
	if (node != 0)
	{
		if (node->m_freeCheckpoint < 0)
		{
			if (m_lock != 0)
				LeaveCriticalSection(m_lock);
			return;
		}
		*link = node->m_next;
		node->m_next = m_current;
		m_current = node;
		m_slots[node->m_freeCheckpoint] = 0;
		if (node->m_description != 0)
			HeapFree(GetProcessHeap(), 0, node->m_description);
	}

	node = m_current;
	if (node != 0)
		m_current = node->m_next;
	else
		node = (Rva008838F0Node *)HeapAlloc(GetProcessHeap(), 4, 0xa4);
	Rva008838F0Node **bucket = &m_buckets[(unsigned int)block % 0x2b7b];
	node->m_next = *bucket;
	*bucket = node;
	node->m_key = (unsigned int)block;
	node->m_type = type;
	node->m_size = size;
	node->m_serial = ++g_Va01336CDC;
	node->m_freeCheckpoint = -1;

	if (format != 0)
	{
		va_list args;
		va_start(args, format);
		if (_vsnprintf(buffer, sizeof(buffer), format, args) < 0)
			buffer[511] = 0;
		va_end(args);
		unsigned int length = (unsigned int)strlen(buffer) + 1;
		node->m_description = HeapAlloc(GetProcessHeap(), 4, length);
		memcpy(node->m_description, buffer, length);
	}
	else
		node->m_description = 0;

	DebugStackwalk::Signature signature;
	node->m_count = DebugStackwalk::StackWalk(signature, 0, false);
	if (node->m_count > 32)
		node->m_count = 32;
	for (unsigned int i = 0; i < node->m_count; ++i)
		node->m_values[i] = signature.GetAddress(i);

	if (m_lock != 0)
		LeaveCriticalSection(m_lock);
}
