// State::~State at 0x000A1B30. Identity: every matched derived state destructor
// (AIGuardIdleState, AIQuarrelState, AIGuardInnerState, ... ) tail-calls
// ??1State@@UAE@XZ through ILT 0x00016725, which routes here. Fuzzy twin
// (tools/fuzzy_twin_scan.py) of Rva007873C0VectorHolderDestructor.cpp: Snapshot
// base-vtable restore (0x01073744) + node-alloc free of the 12-byte-element vector
// at +0x10. novtable keeps State's own (dead) vptr store and vftable out.
// cl: /DNDEBUG /MD /EHsc /O2 /D_STLP_USE_STATIC_LIB
// stlport

#include <memory>
#include "../../Common/System/snapshot.h"

class Rva000A1B30Vector
{
public:
	struct Element { int m_words[3]; };

	~Rva000A1B30Vector()
	{
		Element *begin = m_begin;
		if (begin != 0) {
			unsigned int bytes = (unsigned int)(m_capacityEnd - begin) * sizeof(Element);
			_STL::__node_alloc<true, 0>::deallocate(begin, bytes);
		}
	}

	Element *m_begin;
	Element *m_end;
	Element *m_capacityEnd;
};

class __declspec(novtable) State : public Snapshot
{
public:
	virtual ~State();
	int m_pad04;
	int m_pad08;
	int m_pad0C;
	Rva000A1B30Vector m_vector;
};

// @??1State@@UAE@XZ 0x000A1B30
State::~State()
{
}
