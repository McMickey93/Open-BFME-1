// Two destructors with real bodies over a vector.
//
// The first finishes through a call on this, deletes what a pointer member
// owns and nulls it, and only then lets the vector member go and chains to the
// base. Everything before the state word drops is body: the state stays at its
// starting value across the delete and the null store.
//
// The second walks the vector releasing a reference on every non-null element,
// then the vector itself goes. Its bound is read once into a local before the
// walk, and the element call takes the pointer stored in the slot rather than
// the slot itself.

namespace _STL
{
// retail 0x0082E5F0 is STLport's private node-pool entry; reach it under its real name.
template <bool __threads, int __inst> class __node_alloc;
static void nodePoolDeallocate(void *block, unsigned int bytes);
template <bool __threads, int __inst>
class __node_alloc
{
	friend void nodePoolDeallocate(void *, unsigned int);
	static void __cdecl _M_deallocate(void *__p, unsigned int __n);
};
static inline void nodePoolDeallocate(void *block, unsigned int bytes) { __node_alloc<true, 0>::_M_deallocate(block, bytes); }
}
static inline void bfmeDeallocate(void *block, unsigned int bytes) { _STL::nodePoolDeallocate(block, bytes); }

inline void bfmeRelease(void *block, unsigned int bytes)
{
	if (bytes > 0x80)
		::operator delete(block);
	else
		bfmeDeallocate(block, bytes);
}

class BfmeVecMemberT
{
public:
	~BfmeVecMemberT(void)
	{
		int *start = m_bfmeStart;

		if (start)
			bfmeRelease(start, sizeof(int) * (m_bfmeEnd - start));
	}

private:
	int *m_bfmeStart;					// +0x00
	int *m_bfmeFinish;					// +0x04
	int *m_bfmeEnd;						// +0x08
};

class BfmeOwnedT
{
public:
	virtual ~BfmeOwnedT(void);				// slot +0x00
};

class SubsystemInterface
{
public:
	virtual ~SubsystemInterface(void);				// retail 0x009A1A40

private:
	int m_name;					// +0x04
};

class Gen_0048FA30
{
public:
	void bfmeClear(void);					// retail 0x0048FA30
};

class Gen_00490100 : public SubsystemInterface
{
public:
	virtual ~Gen_00490100(void);

private:
	BfmeOwnedT *m_bfmePtr;					// +0x08
	BfmeVecMemberT m_bfmeVector;				// +0x0C
};

// ??1Gen_00490100@@UAE@XZ
Gen_00490100::~Gen_00490100(void)
{
	reinterpret_cast<Gen_0048FA30 *>(this)->bfmeClear();

	delete m_bfmePtr;

	m_bfmePtr = 0;
}

class TextureBaseClass
{
public:
	void Release_Ref(void);				// retail 0x009EB7A0
};

class BfmeVecBaseS
{
public:
	~BfmeVecBaseS(void)
	{
		TextureBaseClass **start = m_bfmeStart;

		if (start)
			bfmeRelease(start, sizeof(TextureBaseClass *) * (m_bfmeEnd - start));
	}

	TextureBaseClass **m_bfmeStart;				// +0x00
	TextureBaseClass **m_bfmeFinish;				// +0x04
	TextureBaseClass **m_bfmeEnd;				// +0x08
};

class Gen_00757830 : public BfmeVecBaseS
{
public:
	~Gen_00757830(void);
};

// ??1Gen_00757830@@QAE@XZ
Gen_00757830::~Gen_00757830(void)
{
	TextureBaseClass **last = m_bfmeFinish;

	for (TextureBaseClass **it = m_bfmeStart; it != last; ++it)
	{
		if (*it)
			(*it)->Release_Ref();
	}
}
