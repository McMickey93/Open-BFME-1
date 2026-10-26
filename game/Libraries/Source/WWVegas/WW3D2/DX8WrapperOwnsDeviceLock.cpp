// cl: /DNDEBUG /MD /EHsc
// Retail 0x009031A0: current thread owns the DX8 device lock.
// Retail 0x00903070 and 0x009031C0 (unreferenced, after int3 padding) are two
// more queries on the same OwnerThreadId/LockCount pair, address-named:
// whether the lock is free to the current thread (owned by it, or not held),
// and the lock count when the current thread owns it -- otherwise the thread
// id itself comes back, the eax GetCurrentThreadId left.

extern "C" unsigned long __stdcall GetCurrentThreadId(void);

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2/dx8wrapper.h
class DX8Wrapper
{
public:
	static int Owns_Device_Lock(void);

private:
	static unsigned long OwnerThreadId;
	static unsigned LockCount;

public:
	static int rva00903070();
	static unsigned int rva009031C0();
};

// ?Owns_Device_Lock@DX8Wrapper@@SAHXZ
int DX8Wrapper::Owns_Device_Lock(void)
{
	if (GetCurrentThreadId() == OwnerThreadId && LockCount > 0)
		return 1;
	return 0;
}

// ?rva00903070@DX8Wrapper@@SAHXZ
int DX8Wrapper::rva00903070()
{
	if (GetCurrentThreadId() != OwnerThreadId && LockCount != 0)
		return 0;
	return 1;
}

// ?rva009031C0@DX8Wrapper@@SAIXZ
unsigned int DX8Wrapper::rva009031C0()
{
	unsigned result = GetCurrentThreadId();
	if (result == OwnerThreadId)
		result = LockCount;
	return result;
}
