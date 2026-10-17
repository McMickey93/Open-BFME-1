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

class Rva008838F0Node
{
public:
	Rva008838F0Node *m_next;
	unsigned int m_pad04;
	unsigned int m_key;
	unsigned int m_pad0c[2];
	void *m_value14;
	unsigned char m_pad18[0x9c - 0x18];
	int m_freeCheckpoint;
};

class Rva008838F0Owner
{
public:
	void rva008839B0(int type, void *block);
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
		if (old->m_value14 != 0)
		{
			HeapFree(GetProcessHeap(), 0, old->m_value14);
			old->m_value14 = 0;
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

	if (node->m_value14 != 0)
		HeapFree(GetProcessHeap(), 4, node->m_value14);
	if (format != 0)
	{
		va_list args;
		va_start(args, format);
		if (_vsnprintf(buffer, sizeof(buffer), format, args) < 0)
			buffer[511] = 0;
		va_end(args);
		unsigned int length = (unsigned int)strlen(buffer) + 1;
		node->m_value14 = HeapAlloc(GetProcessHeap(), 4, length);
		memcpy(node->m_value14, buffer, length);
	}
	else
		node->m_value14 = 0;

	if (m_lock != 0)
		LeaveCriticalSection(m_lock);
}
