// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// Retail 0x009C4B70 is the cdecl CPU-feature probe called by
// bfmeQueryCpuTierFlags.  CPUID is inline because MSVC 7.1 has no intrinsic
// for it; the surrounding vendor test and SEH remain ordinary C++.
// Keeping the leaf-1 flag test adjacent to CPUID reproduces the retail SEH
// frame and register lifetimes. Moving its result to a C++ local emits 192B
// instead of160B (parent-cpu160 probe), so this short hardware-specific block
// also retains its conditional store and alignment nop.
// The 208-byte row covers the __except filter (0x009C4C10) and handler
// (0x009C4C20) funclets retail places after the body; the handler shape is
// the one Open-BFME-2 matched for the same bytes at its 0x001D5470.

#include <excpt.h>
extern "C" unsigned long __cdecl _exception_code(void);
#define GetExceptionCode _exception_code

extern "C" __declspec(dllimport) int __cdecl strncmp(
	const char *, const char *, unsigned int);

// ?Rva009C4B70CpuFeatureProbe@@YAHXZ
int __cdecl Rva009C4B70CpuFeatureProbe(void)
{
	char vendor[12];
	int result;

	result = 0;
	__try
	{
		__asm
		{
			lea	esi, vendor
			mov	eax, 0
			cpuid
			mov	dword ptr [esi], ebx
			mov	dword ptr [esi+4], edx
			mov	dword ptr [esi+8], ecx
		}
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		unsigned long code = GetExceptionCode();
		if (code)
			return result;
		return result;
	}

	if (strncmp(vendor, "GenuineIntel", 12) == 0
		|| strncmp(vendor, "AuthenticAMD", 12) == 0)
	{
		__asm
		{
			mov	eax, 1
			cpuid
			test	edx, 04000000h
			je	no_sse2
			mov	result, 1
		no_sse2:
			nop
		}
	}

	return result;
}
