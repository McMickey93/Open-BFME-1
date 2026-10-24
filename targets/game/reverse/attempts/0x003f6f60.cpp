// ?method@Rva003F6F60@@YAHPAVPathfindCellInfo@@@Z
// partial score=0.9658 date=2026-10-12
// Retail 0x003F6F60 (146 B): the closed-list walk of Zero Hour's
// PathfindCell::releaseClosedList(list) with releaseInfo() inlined, over BFME
// PathfindCellInfo links (+0x2C next, +0x30 back pointer-to-pointer, +0x24 flags,
// +0x28 cell). Plain intrusive unlink (store through back, reload next, fix
// next->back, clear both), clear flag 8, release the cell's info.
// Probe: 146 bytes, only the count register differs (retail EBP, ours EBX):
// 5 non-reloc bytes (push/xor/inc/mov eax,count/pop). Local order, register,
// unsigned, ++count, do-while, forceinline helpers for the unlink and the
// release, result local and head copy all leave EBX.
// cl: /DNDEBUG /MD /EHsc
class PathfindCell;

class PathfindCellInfo
{
public:
	void releaseToPool(void *pool);

	char m_pad00[0x24];
	unsigned int m_flags;
	PathfindCell *m_cell;
	PathfindCellInfo *m_next;
	PathfindCellInfo **m_back;
};

class PathfindCell
{
public:
	PathfindCellInfo *m_info;
	char m_pad04[8];
	unsigned int m_packed;
};

extern PathfindCellInfo *g_bfmePathfindFreeList;

namespace Rva003F6F60
{
int method(PathfindCellInfo *list)
{
	if (list == 0)
		return 0;
	int count = 0;
	while (list)
	{
		count++;
		PathfindCellInfo *cur = list;
		list = cur->m_next;
		if (cur->m_back)
		{
			*cur->m_back = cur->m_next;
			if (cur->m_next)
				cur->m_next->m_back = cur->m_back;
			cur->m_back = 0;
			cur->m_next = 0;
		}
		cur->m_flags &= ~8u;
		PathfindCell *cell = cur->m_cell;
		if (cell)
		{
			unsigned int packed = cell->m_packed;
			if ((packed & 7) != 4 && (packed & 0x38) == 0 &&
				(packed & 0x80000) == 0 && cell->m_info != 0 &&
				cell->m_info->m_back == 0 &&
				(cell->m_info->m_flags & 0x18) == 0)
			{
				cell->m_info->releaseToPool(&g_bfmePathfindFreeList);
				cell->m_info = 0;
			}
		}
	}
	return count;
}
}
