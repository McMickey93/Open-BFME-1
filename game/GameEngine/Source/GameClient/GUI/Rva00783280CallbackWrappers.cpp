// cl: /DNDEBUG /MD /EHsc
extern void j_0001df43(void);
class WindowManager
{
public:
	void invokeCallback(const char *name, void *unused);
	void invokeCallbackWithArg_0046CE60(const char *name, void *context);
	void method_0046CF80(const char *name);
};

extern WindowManager *g_rva012F19E8WindowManager;	// retail [0x012F19E8]

// ?Rva00783280InvokeCallback@@YAXPBDPAX@Z
void Rva00783280InvokeCallback(const char *name, void *unused)
{
	g_rva012F19E8WindowManager->invokeCallback(name, unused);
}

// ?Rva007832D0@@YAXPBD@Z
void Rva007832D0(const char *name)
{
	struct Rva0046CF80Thunk
{
	void call(const char *name);
};
typedef void (Rva0046CF80Thunk::*Rva0046CF80Call)(const char *name);
	union
	{
		void (*asFunction)();
		Rva0046CF80Call asMember;
	} functionCast;
	functionCast.asFunction = j_0001df43;
	(((Rva0046CF80Thunk *)g_rva012F19E8WindowManager)->*functionCast.asMember)(name);
}

// ?Rva007832B0InvokeCallbackWithArg@@YAXPBDPAX@Z
void Rva007832B0InvokeCallbackWithArg(const char *name, void *context)
{
	g_rva012F19E8WindowManager->invokeCallbackWithArg_0046CE60(name, context);
}

// Handler slot 15 installed by bfmeInstallHandlersVB (DIR32 0x007894DC,
// recorded there as bfmeHandler15VB): deletes the object through its virtual
// destructor when any of the 0x406 flag bits is set.
class Rva007832F0Object
{
public:
	virtual ~Rva007832F0Object();
};

// ?Rva007832F0@@YAXPAVRva007832F0Object@@I@Z
void Rva007832F0(Rva007832F0Object *object, unsigned int flags)
{
	if ((flags & 0x406) && object)
		delete object;
}

// Handler slot 24 (DIR32 0x00789536, recorded as bfmeHandler24VB): returns a
// block to its memory pool.
class MemoryPool
{
public:
	void freeBlock(void *block);
};

// ?Rva00786C90@@YAXPAVMemoryPool@@PAX@Z
void Rva00786C90(MemoryPool *pool, void *block)
{
	pool->freeBlock(block);
}
