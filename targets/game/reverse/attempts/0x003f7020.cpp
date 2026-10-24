// ?method@Rva003F7020@@YAHPAX@Z
// partial score=0.9658 date=2026-10-16
class PathfindCell;
struct PathfindCellInfo
{
	char m_pad00[0x24];
	unsigned int m_flags;
	PathfindCell *m_cell;
	PathfindCellInfo *m_next;
	PathfindCellInfo **m_back;
	void unlink()
	{
		if (m_back)
		{
			*m_back = m_next;
			if (m_next)
				m_next->m_back = m_back;
			m_back = 0;
			m_next = 0;
		}
	}
};
struct PathfindCell { PathfindCellInfo *m_info; char p[8]; unsigned int m_packed; };
struct Pool { void releaseInto(void *head); };
extern int g_bfmePathfindFreeList;
namespace Rva003F7020 {
int method(void *p)
{
	PathfindCellInfo *list = (PathfindCellInfo *)p;
	if (list == 0) return 0;
	int count = 0;
	while (list)
	{
		++count;
		PathfindCellInfo *cur = list;
		list = cur->m_next;
		cur->unlink();
		cur->m_flags &= ~0x10u;
		PathfindCell *cell = cur->m_cell;
		if (cell)
		{
			unsigned int packed = cell->m_packed;
			if ((packed & 7) != 4 && (packed & 0x38) == 0 && (packed & 0x80000) == 0 &&
				cell->m_info && cell->m_info->m_back == 0 && (cell->m_info->m_flags & 0x18) == 0)
			{
				((Pool *)cell->m_info)->releaseInto(&g_bfmePathfindFreeList);
				cell->m_info = 0;
			}
		}
	}
	return count;
}
}
